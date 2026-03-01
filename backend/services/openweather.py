import os
import requests


def get_weather_openweather(lat: float, lon: float) -> dict:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {
            "source": "OpenWeatherMap",
            "temperature": None,
            "wind_speed": None,
            "error": "OPENWEATHER_API_KEY не задан в .env",
        }
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "lang": "ru",
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "source": "OpenWeatherMap",
            "temperature": data.get("main", {}).get("temp"),
            "wind_speed": data.get("wind", {}).get("speed"),
        }
    except requests.RequestException as e:
        return {
            "source": "OpenWeatherMap",
            "temperature": None,
            "wind_speed": None,
            "error": str(e),
        }