from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / "api.env")

from backend.services.aggregator import get_weather_all_sources
from backend.services.geocoding import geocode_first
from backend.services.dwd_icon import get_forecast_dwd_icon
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # разрешает запросы с любых origin (для разработки)


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
        coords = geocode_first(city)
        if not coords:
            return jsonify({"error": "Город не найден"}), 404
        lat, lon, _ = coords
        sources = get_weather_all_sources(lat, lon)
        return jsonify({"sources": sources})

    return jsonify({"error": "Укажите city= или lat= и lon="}), 400


@app.route("/api/forecast", methods=["GET"])
def api_forecast():
    lat, lon, timezone = _get_lat_lon_timezone()
    if lat is None or lon is None:
        return jsonify({"error": "Укажите city= или lat= и lon="}), 400
    days = request.args.get("days", type=int, default=7)
    result = get_forecast_dwd_icon(lat, lon, days=days, timezone=timezone)
    if result.get("error"):
        return jsonify({"error": result["error"]}), 502
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 
