from backend.services.open_meteo import get_weather_open_meteo
from backend.services.openweather import get_weather_openweather
from backend.services.dwd_icon import get_current_weather_dwd_icon


def _dwd_icon_result(lat: float, lon: float) -> dict:
    """Вызов DWD ICON с защитой от любых исключений — всегда возвращаем карточку источника."""
    try:
        return get_current_weather_dwd_icon(lat, lon)
    except Exception as e:
        return {
            "source": "DWD ICON",
            "temperature": None,
            "wind_speed": None,
            "wind_direction": None,
            "wind_gusts": None,
            "error": f"Временная ошибка: {e!s}",
        }


def get_weather_all_sources(lat: float, lon: float) -> list:
    # Порядок: DWD ICON первый (основной интерес), затем Open-Meteo и OpenWeatherMap.
    # Всегда возвращаем 3 источника; при ошибке DWD — карточка с полем "error".
    results = []
    results.append(_dwd_icon_result(lat, lon))
    results.append(get_weather_open_meteo(lat, lon))
    results.append(get_weather_openweather(lat, lon))
    return results