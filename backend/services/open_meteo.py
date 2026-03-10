import requests

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_open_meteo(lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m",
        "wind_speed_unit": "ms",
    }
    resp = requests.get(FORECAST_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    current = data.get("current", {})
    return {
        "source": "Open-Meteo",
        "temperature": current.get("temperature_2m"),
        "wind_speed": current.get("wind_speed_10m"),
    }


def get_forecast_open_meteo_fallback(
    lat: float,
    lon: float,
    days: int = 7,
    timezone: str = "auto",
) -> dict:
    """
    Прогноз через обычный Open-Meteo, когда DWD ICON недоступен.
    Возвращает структуру, совместимую с get_forecast_dwd_icon: daily, wind_by_height (только 10 м).
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": timezone,
        "forecast_days": min(max(days, 1), 16),
        "hourly": "temperature_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
        "daily": "temperature_2m_max,temperature_2m_min,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,precipitation_sum,weather_code",
        "wind_speed_unit": "ms",
    }
    try:
        resp = requests.get(FORECAST_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return {"error": str(e), "daily": [], "wind_by_height": []}

    hourly = data.get("hourly", {})
    daily = data.get("daily", {})
    times = hourly.get("time", [])

    current = {}
    if times:
        current = {
            "temperature": _at(hourly.get("temperature_2m"), 0),
            "wind_speed_10m": _at(hourly.get("wind_speed_10m"), 0),
            "wind_direction_10m": _at(hourly.get("wind_direction_10m"), 0),
            "wind_gusts_10m": _at(hourly.get("wind_gusts_10m"), 0),
        }

    wind_by_height = []
    s10 = _at(hourly.get("wind_speed_10m"), 0)
    d10 = _at(hourly.get("wind_direction_10m"), 0)
    if s10 is not None or d10 is not None:
        wind_by_height.append({"height_label": "10 м", "height_m": 10, "speed": s10, "direction": d10})

    daily_times = daily.get("time", [])
    days_list = []
    for i in range(len(daily_times)):
        days_list.append({
            "date": daily_times[i],
            "temperature_2m_max": _at(daily.get("temperature_2m_max"), i),
            "temperature_2m_min": _at(daily.get("temperature_2m_min"), i),
            "wind_speed_10m_max": _at(daily.get("wind_speed_10m_max"), i),
            "wind_gusts_10m_max": _at(daily.get("wind_gusts_10m_max"), i),
            "wind_direction_10m_dominant": _at(daily.get("wind_direction_10m_dominant"), i),
            "precipitation_sum": _at(daily.get("precipitation_sum"), i),
            "weather_code": _at(daily.get("weather_code"), i),
        })

    return {
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "timezone": data.get("timezone"),
        "current": current,
        "daily": days_list,
        "hourly_preview": [],
        "wind_by_height": wind_by_height,
        "forecast_note": "Прогноз: Open-Meteo (DWD ICON недоступен).",
    }


def _at(arr, index):
    if not arr or index >= len(arr):
        return None
    return arr[index]