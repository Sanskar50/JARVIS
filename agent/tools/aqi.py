from agent.schemas.tools import WebSearchInput
from agent.config import config
import requests


def get_aqi(input_data: WebSearchInput):
    """
    function to get temperature data.
    """
    mapping = {
        1: "Good",
        2: "Moderate",
        3: "Unhealthy for sensitive group",
        4: "Unhealthy",
        5: "Very Unhealthy",
        6: "Hazardous",
    }
    try:
        url = f"{config.WEATHER_API_BASE_URL}/forecast.json?key={config.API_KEY}&q={input_data['location']}&aqi=yes"
        response = requests.get(url)
        aqi_data = response.json()
        return {aqi_data["current"]["air_quality"]["us-epa-index"]:mapping[aqi_data["current"]["air_quality"]["us-epa-index"]]}
    except Exception as e:
        return str(e)
