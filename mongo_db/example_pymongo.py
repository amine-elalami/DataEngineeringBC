from datetime import datetime
import asyncio
import requests
import os
from pymongo import MongoClient
from pprint import pprint
from dotenv import load_dotenv

env = load_dotenv()
KEY = os.environ.get("OPENWEATHER_KEY")

async def get_weather(city):
    r = requests.get(
        url="https://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(
            city,
            KEY
        )
    )
    return r.json()


CITIES = [
    "London", "Paris", "New York", "Tokyo", "Sydney", "Toulouse", "Lyon",
    "Marseille", "Bordeaux", "Nantes", "Strasbourg", "Montpellier",
    "Nice", "Lille", "Rennes", "Reims", "Le Havre", "Saint-Étienne", "Toulon", "Grenoble"
]

async def get_clean_data():
    results = await asyncio.gather(*(get_weather(city) for city in CITIES))
    clean_data = []
    for r_data in results:
        if r_data.get("cod") != 200:
            print(r_data)
        else:
            clean_data.append({
                "main": r_data["main"],
                "weather": r_data["weather"],
                "city": r_data["name"],
                "time": datetime.fromtimestamp(r_data["dt"]).strftime("%H:%M:%S")
                })
    return clean_data

async def main():
    client = MongoClient(
        host = "127.0.0.1",
        port = 27017,
        username = "datascientest",
        password = "dst123"
    )
    clean_data = await get_clean_data()
    if not clean_data:
        print("Aucune donnée à insérer dans la base de données.")
        return
    sample = client['sample']
    if "weather" in sample.list_collection_names():
        sample.drop_collection("weather")
    weather = sample.create_collection(name="weather")
    weather = sample['weather']
    weather.insert_many(clean_data)
    pprint(weather.find({"weather.main": "Clear"}, {"_id": 0, "city": 1}).to_list())
    pprint(weather.count_documents({
        "$and": [
            {"main.temp_min": {"$gte": 287}},
            {"main.temp_max": {"$lte": 291}}]
            }))

    pprint(weather.aggregate([
        # {"$match": {"main.temp_min": {"$gte": 287, "$lte": 291}}},
        {"$group": {"_id": "$weather.main", "count": {"$sum": 1}}}
    ]).to_list())

if __name__ == "__main__":
    asyncio.run(main())
