import json
import re
from google import genai
from agent.tools.weather import get_weather
from agent.tools.temp import get_temperature
from agent.tools.aqi import get_aqi
from agent.config import config
from rich.console import Console
from rich.table import Table
from io import StringIO


class AgentController:
    def __init__(self):
        self.tools = {
            "get_weather": get_weather,
            "get_temperature": get_temperature,
            "get_aqi": get_aqi,
        }

    def get_weather(self, location: str):
        return self.tools.get("get_weather")({"location": location})

    def get_temperature(self, location: str):
        return self.tools.get("get_temperature")({"location": location})

    def get_aqi(self, location: str):
        return self.tools.get("get_aqi")({"location": location})

    def extract_json(self, text: str):
        # Remove code fences if present
        text = text.strip()
        fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if fenced:
            text = fenced.group(1)
        return json.loads(text)

    def _load_prompt(self, prompt_name: str):
        try:
            with open(f"agent/prompts/{prompt_name}.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"{prompt_name} prompt file not found, using default.")
            return "You are a helpful assistant."

    def call_gemma(self, prompt):
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        try:
            response = client.models.generate_content(
                model=config.GEMINI_MODEL_NAME,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            return f"Error generating alerts: {str(e)}"

    def format_output_rich(self, data):
        """Formats the final output as a proper table using the 'rich' library."""
        if not data:
            return "No data to display."
        # Initialize Rich console to capture output
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True)
        table = Table(
            show_header=True, header_style="bold magenta", border_style="blue"
        )
        if isinstance(data, list) and len(data) > 0:
            # Assuming data is a list of dictionaries
            headers = list(data[0].keys())
            for header in headers:
                table.add_column(header.capitalize(), style="cyan", max_width=50)
            for item in data:   
                row_values = [str(item.get(header, "")) for header in headers]
                table.add_row(*row_values)
        elif isinstance(data, dict):
            # If it's a single dictionary
            table.add_column("Property", style="bold green")
            table.add_column("Value", style="yellow")
            for key, value in data.items():
                table.add_row(str(key).capitalize(), str(value))
        else:
            # For other types of data
            return str(data)
        console.print(table)
        return string_io.getvalue()

    def process_request(self, user_input: str):
        """
        Processes a user request through a multi-step agentic workflow.

        Steps:
        1.  **Prompt Assembly**: Loads system, function calling, and output prompts.
            Combines them with user input for the initial LLM call.
        2.  **Initial LLM Call**: Calls the LLM to determine if any external tools
            are needed to fulfill the request.
        3.  **JSON Extraction**: Parses the LLM's response to extract structured
            tool call data.
        4.  **Tool Execution** (Conditional):
            - If tools are requested: Iterates through each tool call, executes the
              corresponding function, and collects the returned data.
            - **Second LLM Call**: Re-prompts the LLM with the original request,
              the retrieved tool data, and formatting instructions to generate
              the final response.
        5.  **Direct Processing** (Conditional):
            - If no tools are requested: Calls the LLM directly with the output
              prompt to generate a response from its internal knowledge.
        6.  **Final Formatting**: Extracts JSON from the final response and applies
            rich terminal formatting (tables/headers) via `format_output_rich`.
        7.  **Result Delivery**: Returns the polished, formatted string to the caller.

        Args:
            user_input (str): The raw text query from the user.

        Returns:
            str: The final formatted response or an error message if processing fails.
        """
        try:
            system_prompt = self._load_prompt("system")
            function_calling_prompt = self._load_prompt("function_calling")
            output_prompt = self._load_prompt("output")
            prompt = (
                f"{system_prompt}\n{function_calling_prompt}\nUser Input: {user_input}"
            )
            final_result = ""
            api_results = ""
            llm_response = self.call_gemma(prompt)
            llm_result = self.extract_json(llm_response)
            if llm_result:
                for call in llm_result:
                    function_name = call["function"]
                    function_args = call["arguments"]
                    result = self.tools.get(function_name)(function_args)
                    api_results += result
                final_result = self.extract_json(
                    self.call_gemma(
                        f"{system_prompt}\n User Input: {user_input}\n The required external data has already been retrieved here \n Api Results: {api_results}.\n Output prompt:{output_prompt}"
                    )
                )
            else:
                final_result = self.extract_json(
                    self.call_gemma(f"{user_input}\n Output prompt:{output_prompt}")
                )
            formatted_result = self.format_output_rich(final_result)
            return formatted_result.strip()
        except Exception as e:
            return f"Error processing request: {str(e)}"

    def run(self):
        print("Agent Controller started.")
