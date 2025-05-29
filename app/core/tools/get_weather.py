import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from datetime import datetime
from langchain_core.tools import Tool

load_dotenv()

api_key = os.getenv("OPENWEATHER_API_KEY", "")
base_url = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_func(city_name: str = "") -> str:
    """
    Get current weather information for a specific city or based on IP location if no city is provided.
    
    Args:
        city_name (str): Name of the city to get weather for. If empty, uses IP location.
        
    Returns:
        str: Weather information as a formatted string
    """
    params: Dict[str, Any] = {
        "appid": api_key,
        "units": "metric"  
    }
    
    # If city name is provided, use it for the query
    if city_name and city_name.strip():
        params["q"] = city_name.strip()
    else:
        # Otherwise use IP location
        try:
            loc = requests.get("https://ipinfo.io/json").json().get("loc", "").split(",")
            lat, lon = map(float, loc) if loc else (None, None)
            
            if lat is None or lon is None:
                return "Could not determine your location. Please provide a city name."
                
            params["lat"] = lat
            params["lon"] = lon
        except Exception as e:
            return f"Error determining location: {str(e)}. Please provide a city name."

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        
        result = {
            "location": f"{weather_data['name']}, {weather_data['sys']['country']}",
            "temperature": f"{weather_data['main']['temp']}°C",
            "feels_like": f"{weather_data['main']['feels_like']}°C",
            "humidity": f"{weather_data['main']['humidity']}%",
            "pressure": f"{weather_data['main']['pressure']} hPa",
            "wind_speed": f"{weather_data['wind']['speed']} m/s",
            "weather_main": weather_data['weather'][0]['main'],
            "weather_description": weather_data['weather'][0]['description'],
            "datetime": datetime.fromtimestamp(weather_data['dt']).strftime('%Y-%m-%d %H:%M:%S') if 'dt' in weather_data else None
        }

        semantic_result = f"Weather information for {result.get('location', 'Unknown Location')}:\n"
        semantic_result += f"- Current temperature: {result.get('temperature', 'N/A')}\n"
        semantic_result += f"- Feels like: {result.get('feels_like', 'N/A')}\n"
        semantic_result += f"- Conditions: {result.get('weather_description', 'N/A')}\n"
        semantic_result += f"- Humidity: {result.get('humidity', 'N/A')}\n"
        semantic_result += f"- Wind speed: {result.get('wind_speed', 'N/A')}\n"
        semantic_result += f"- Pressure: {result.get('pressure', 'N/A')}\n"
        semantic_result += f"- Time: {result.get('datetime', 'N/A')}"
            
        return semantic_result
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            return f"City '{city_name}' not found. Please check the spelling or try another city."
        else:
            return f"Error retrieving weather data: {str(err)}"
    except Exception as e:
        return f"Error: {str(e)}"

get_weather = Tool(
    name="get_weather",
    description="Get current weather information for a city. If no city is provided, uses your current location based on IP address.",
    func=get_weather_func
)
