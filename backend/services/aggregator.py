from backend.services.open_meteo import get_weather_open_meteo
from backend.services.openweather import get_weather_openweather
from backend.services.dwd_icon import get_current_weather_dwd_icon


def get_weather_all_sources(lat: float, lon: float) -> list:
    results = []
    results.append(get_weather_open_meteo(lat, lon))
    results.append(get_weather_openweather(lat, lon))
    results.append(get_current_weather_dwd_icon(lat, lon))
    return results