from backend.services.open_meteo import get_weather_open_meteo
from backend.services.openweather import get_weather_openweather


def get_weather_all_sources(lat: float, lon: float) -> list:
    results = []
    results.append(get_weather_open_meteo(lat, lon))
    results.append(get_weather_openweather(lat, lon))
    return results