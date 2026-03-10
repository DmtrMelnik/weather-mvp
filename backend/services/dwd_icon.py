import requests

DWD_ICON_URL = "https://api.open-meteo.com/v1/dwd-icon"

HOURLY_WIND_FIXED = (
    "temperature_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m,"
    "wind_speed_80m,wind_direction_80m,wind_speed_120m,wind_direction_120m,"
    "wind_speed_180m,wind_direction_180m"
)
HOURLY_WIND_WITH_PRESSURE = (
    HOURLY_WIND_FIXED + ","
    "wind_speed_1000hPa,wind_direction_1000hPa,wind_speed_975hPa,wind_direction_975hPa,"
    "wind_speed_950hPa,wind_direction_950hPa,wind_speed_925hPa,wind_direction_925hPa,"
    "wind_speed_900hPa,wind_direction_900hPa"
)
DAILY_FORECAST = (
    "temperature_2m_max,temperature_2m_min,wind_speed_10m_max,wind_gusts_10m_max,"
    "wind_direction_10m_dominant,precipitation_sum,weather_code"
)

# Ветер по высотам: фиксированные (м) и уровни давления (приблизительно над уровнем моря)
WIND_HEIGHT_KEYS = [
    ("10 м", "wind_speed_10m", "wind_direction_10m", 10),
    ("80 м", "wind_speed_80m", "wind_direction_80m", 80),
    ("120 м", "wind_speed_120m", "wind_direction_120m", 120),
    ("180 м", "wind_speed_180m", "wind_direction_180m", 180),
]
WIND_PRESSURE_KEYS = [
    ("~110 м (1000 hPa)", "wind_speed_1000hPa", "wind_direction_1000hPa", 110),
    ("~320 м (975 hPa)", "wind_speed_975hPa", "wind_direction_975hPa", 320),
    ("~500 м (950 hPa)", "wind_speed_950hPa", "wind_direction_950hPa", 500),
    ("~800 м (925 hPa)", "wind_speed_925hPa", "wind_direction_925hPa", 800),
    ("~1000 м (900 hPa)", "wind_speed_900hPa", "wind_direction_900hPa", 1000),
]


def get_current_weather_dwd_icon(lat: float, lon: float) -> dict:
    """Текущая погода из DWD ICON для агрегатора (формат как open_meteo)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
    }
    try:
        resp = requests.get(DWD_ICON_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        cur = data.get("current", {})
        return {
            "source": "DWD ICON",
            "temperature": cur.get("temperature_2m"),
            "wind_speed": cur.get("wind_speed_10m"),
            "wind_direction": cur.get("wind_direction_10m"),
            "wind_gusts": cur.get("wind_gusts_10m"),
        }
    except requests.RequestException as e:
        return {
            "source": "DWD ICON",
            "temperature": None,
            "wind_speed": None,
            "wind_direction": None,
            "wind_gusts": None,
            "error": str(e),
        }


def get_forecast_dwd_icon(
    lat: float,
    lon: float,
    days: int = 7,
    timezone: str = "auto",
) -> dict:
    """
    Прогноз на неделю: текущая погода, по дням, почасовой ветер и ветер по высотам.
    Сначала запрашиваем с уровнями давления; при ошибке — только фиксированные высоты.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": timezone,
        "forecast_days": min(max(days, 1), 10),
        "hourly": HOURLY_WIND_WITH_PRESSURE,
        "daily": DAILY_FORECAST,
    }
    try:
        resp = requests.get(DWD_ICON_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        use_pressure_heights = True
    except requests.RequestException:
        params["hourly"] = HOURLY_WIND_FIXED
        try:
            resp = requests.get(DWD_ICON_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            use_pressure_heights = False
        except requests.RequestException as e:
            return {"error": str(e), "daily": [], "wind_by_height": []}

    hourly = data.get("hourly", {})
    daily = data.get("daily", {})
    times = hourly.get("time", [])

    # Текущий момент: первый час
    current = {}
    if times:
        idx = 0
        current = {
            "temperature": _at(hourly.get("temperature_2m"), idx),
            "wind_speed_10m": _at(hourly.get("wind_speed_10m"), idx),
            "wind_direction_10m": _at(hourly.get("wind_direction_10m"), idx),
            "wind_gusts_10m": _at(hourly.get("wind_gusts_10m"), idx),
        }

    # Ветер по высотам для текущего часа (индекс 0): фиксированные высоты + уровни давления
    wind_by_height = []
    for label, speed_key, dir_key, height_m in WIND_HEIGHT_KEYS:
        speed = _at(hourly.get(speed_key), 0)
        direction = _at(hourly.get(dir_key), 0)
        wind_by_height.append({
            "height_label": label,
            "height_m": height_m,
            "speed": speed,
            "direction": direction,
        })
    if use_pressure_heights:
        for label, speed_key, dir_key, height_m in WIND_PRESSURE_KEYS:
            speed = _at(hourly.get(speed_key), 0)
            direction = _at(hourly.get(dir_key), 0)
            wind_by_height.append({
                "height_label": label,
                "height_m": height_m,
                "speed": speed,
                "direction": direction,
            })

    # Почасовой ветер на первые 48 часов (опционально для фронта)
    hourly_slice = []
    for i in range(min(48, len(times))):
        hourly_slice.append({
            "time": times[i],
            "temperature_2m": _at(hourly.get("temperature_2m"), i),
            "wind_speed_10m": _at(hourly.get("wind_speed_10m"), i),
            "wind_direction_10m": _at(hourly.get("wind_direction_10m"), i),
            "wind_gusts_10m": _at(hourly.get("wind_gusts_10m"), i),
            "wind_speed_80m": _at(hourly.get("wind_speed_80m"), i),
            "wind_speed_120m": _at(hourly.get("wind_speed_120m"), i),
            "wind_speed_180m": _at(hourly.get("wind_speed_180m"), i),
        })

    # Дни
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
        "hourly_preview": hourly_slice,
        "wind_by_height": wind_by_height,
    }


def _at(arr, index):
    if not arr or index >= len(arr):
        return None
    return arr[index]
