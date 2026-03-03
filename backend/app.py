# Практика: добавлен комментарий для коммита
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / "api.env")

from backend.services.aggregator import get_weather_all_sources
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # разрешает запросы с любых origin (для разработки)



@app.route("/api/weather", methods=["GET"])
def api_weather():
    # Поддержка и city= и lat= & lon=
    city = request.args.get("city")
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is not None and lon is not None:
        # Пока один источник — агрегатор просто возвращает его результат
        sources = get_weather_all_sources(lat, lon)
        return jsonify({"sources": sources})

    if city:
        sources = get_weather_all_sources(52.52, 13.41)
        return jsonify({
            "sources": sources,
            "note": "По городу «Берлин» пока заглушка. Геокодинг добавим позже.",
        })

    return jsonify({"error": "Укажите city= или lat= и lon="}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 
