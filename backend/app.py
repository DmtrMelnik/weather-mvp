from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # разрешает запросы с любых origin (для разработки)

# Заглушка: один источник погоды (Open-Meteo)
def get_weather_open_meteo(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m",
        "hourly": "temperature_2m,wind_speed_10m",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    current = data.get("current", {})
    return {
        "source": "Open-Meteo",
        "temperature": current.get("temperature_2m"),
        "wind_speed": current.get("wind_speed_10m"),
    }


@app.route("/api/weather", methods=["GET"])
def api_weather():
    # Поддержка и city= и lat= & lon=
    city = request.args.get("city")
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is not None and lon is not None:
        # Пока один источник — агрегатор просто возвращает его результат
        result = get_weather_open_meteo(lat, lon)
        return jsonify({"sources": [result]})

    if city:
        # Упрощение: для города берём координаты Берлина (позже можно добавить геокодинг)
        return jsonify({
            "sources": [get_weather_open_meteo(52.52, 13.41)],
            "note": f"По городу «{city}» пока возвращаем заглушку (Берлин). Добавим геокодинг позже.",
        })

    return jsonify({"error": "Укажите city= или lat= и lon="}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)