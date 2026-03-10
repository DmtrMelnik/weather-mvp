import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def geocode(city: str, lang: str = "ru", count: int = 5) -> list[dict]:
    """Возвращает список совпадений по названию города."""
    if not city or len(city.strip()) < 2:
        return []
    params = {
        "name": city.strip(),
        "count": count,
        "language": lang,
    }
    try:
        resp = requests.get(GEOCODING_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except requests.RequestException:
        return []


def geocode_first(city: str, lang: str = "ru") -> tuple[float, float, str] | None:
    """
    Возвращает (latitude, longitude, timezone) первого результата или None.
    """
    results = geocode(city, lang=lang, count=1)
    if not results:
        return None
    r = results[0]
    return (
        float(r["latitude"]),
        float(r["longitude"]),
        r.get("timezone", "auto"),
    )
