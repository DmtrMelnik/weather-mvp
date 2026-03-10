from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / "api.env")

from backend.services.aggregator import get_weather_all_sources
from backend.services.geocoding import geocode_first, geocode_first_with_location
from backend.services.dwd_icon import get_forecast_dwd_icon
from backend.services.open_meteo import get_forecast_open_meteo_fallback
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Явно разрешаем запросы с любого origin (localhost, Vercel и т.д.)
CORS(app, resources={r"/api/*": {"origins": "*"}})


def _get_lat_lon_timezone():
    """Возвращает (lat, lon, timezone) из city или lat/lon. При ошибке — (None, None, None)."""
    city = request.args.get("city")
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    if lat is not None and lon is not None:
        return lat, lon, "auto"
    if city:
        coords = geocode_first(city)
        if coords:
            return coords[0], coords[1], coords[2]
    return None, None, None


@app.route("/api/weather", methods=["GET"])
def api_weather():
    city = request.args.get("city")
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is not None and lon is not None:
        sources = get_weather_all_sources(lat, lon)
        return jsonify({"sources": sources})

    if city:
        location = geocode_first_with_location(city)
        if not location:
            return jsonify({"error": "Город не найден"}), 404
        lat, lon = location["latitude"], location["longitude"]
        sources = get_weather_all_sources(lat, lon)
        payload = {"sources": sources, "location": {"name": location["name"], "country": location["country"], "country_code": location["country_code"], "latitude": lat, "longitude": lon}}
        return jsonify(payload)

    return jsonify({"error": "Укажите city= или lat= и lon="}), 400


@app.route("/api/forecast", methods=["GET"])
def api_forecast():
    city = request.args.get("city")
    lat, lon, timezone = _get_lat_lon_timezone()
    if lat is None or lon is None:
        return jsonify({"error": "Укажите city= или lat= и lon="}), 400
    days = request.args.get("days", type=int, default=7)
    result = get_forecast_dwd_icon(lat, lon, days=days, timezone=timezone)
    if result.get("error"):
        # При недоступности DWD ICON отдаём прогноз через обычный Open-Meteo (200, а не 502)
        fallback = get_forecast_open_meteo_fallback(lat, lon, days=days, timezone=timezone)
        if not fallback.get("error"):
            if city:
                loc = geocode_first_with_location(city)
                if loc:
                    fallback["location"] = {"name": loc["name"], "country": loc["country"], "country_code": loc["country_code"], "latitude": lat, "longitude": lon}
            return jsonify(fallback)
        return jsonify({"error": result["error"], "daily": [], "wind_by_height": []}), 200
    if city:
        loc = geocode_first_with_location(city)
        if loc:
            result["location"] = {"name": loc["name"], "country": loc["country"], "country_code": loc["country_code"], "latitude": lat, "longitude": lon}
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 
