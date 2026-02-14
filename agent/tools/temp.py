import requests
from agent.config import config


def get_temperature(input_data: {"location": "Bengaluru"}):
    try:
        url = f"{config.WEATHER_API_BASE_URL}/forecast.json?key={config.API_KEY}&q={input_data['location']}"
        response = requests.get(url)
        result = response.json()
        return f"{input_data['location']}: Maximum Temperature: {result['forecast']['forecastday'][0]['day']['maxtemp_c']}, Minimum Temperature: {result['forecast']['forecastday'][0]['day']['mintemp_c']}"
    except Exception as e:
        return str(e)
