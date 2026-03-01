import requests

url = "https://api.open-meteo.com/v1/dwd-icon"

params = {
    "latitude": 50.11,
    "longitude": 8.68,
    "hourly": "temperature_2m,wind_speed_10m"
}

response = requests.get(url, params=params)
data = response.json()

print("Температура:", data["hourly"]["temperature_2m"][:5])
print("Ветер:", data["hourly"]["wind_speed_10m"][:5])