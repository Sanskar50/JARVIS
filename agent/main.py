import sys
import os

# Ensure the project root is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent_controller import AgentController


def main():
    print("Starting Agent Application...")
    controller = AgentController()
    # Example usage
    try:
        controller.run()
        print(
            "I am a JARVIS an AI Assistant. I can help you with your queries.\nEnter your query:"
        )
        user_input = input()
        response = controller.process_request(user_input)
        print(f"\n{response}")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
