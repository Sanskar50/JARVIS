import requests
from agent.config import config


def get_weather(input_data: {"location": "Bengaluru"}):
    """
    function to get temperature data.
    """
    try:
        url = f"{config.WEATHER_API_BASE_URL}/forecast.json?key={config.API_KEY}&q={input_data['location']}"
        response = requests.get(url)
        weather_data = response.json()
        return f"{input_data['location']}: {weather_data['current']['condition']['text']}"
    except Exception as e:
        return str(e)
