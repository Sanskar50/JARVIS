from agent.schemas.tools import WeatherToolInput

def get_weather(input_data: WeatherToolInput):
    """
    Mock function to get weather data.
    """
    # In a real app, this would call an API
    return {
        "location": input_data.location,
        "temperature": 22,
        "unit": input_data.unit,
        "condition": "Sunny"
    }
