import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def geocode(city: str, lang: str = "ru", count: int = 10) -> list[dict]:
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


def _sort_by_population(results: list[dict]) -> list[dict]:
    """Сортировка по населению (сначала крупные города), без population — в конец."""
    def key(r):
        p = r.get("population")
        if p is None:
            return 0
        try:
            return int(p)
        except (TypeError, ValueError):
            return 0
    return sorted(results, key=key, reverse=True)


def geocode_first(city: str, lang: str = "ru") -> tuple[float, float, str] | None:
    """
    Возвращает (latitude, longitude, timezone) лучшего совпадения или None.
    Берём несколько результатов, сортируем по населению — выбирается крупнейший город с таким названием.
    """
    detail = geocode_first_with_location(city, lang=lang)
    if not detail:
        return None
    return (
        detail["latitude"],
        detail["longitude"],
        detail.get("timezone", "auto"),
    )


def geocode_first_with_location(city: str, lang: str = "ru") -> dict | None:
    """
    Возвращает один результат с полной информацией о месте для корректного отображения.
    Приоритет — город с наибольшим населением (чтобы «Минск» давал Минск, Беларусь, а не мелкий одноимённый населённый пункт).
    """
    results = geocode(city, lang=lang, count=10)
    if not results:
        return None
    sorted_results = _sort_by_population(results)
    r = sorted_results[0]
    return {
        "latitude": float(r["latitude"]),
        "longitude": float(r["longitude"]),
        "timezone": r.get("timezone", "auto"),
        "name": r.get("name", city.strip()),
        "country": r.get("country", ""),
        "country_code": r.get("country_code", ""),
    }
