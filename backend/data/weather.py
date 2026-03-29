import pandas as pd
from ..db import engine
from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime, timezone
import openmeteo_requests
import requests_cache
from retry_requests import retry

# NYISO zones mapped to representative city coordinates
NYISO_ZONES = {
    "CAPITL":  {"latitude": 42.65, "longitude": -73.75},   # Albany
    "CENTRL":  {"latitude": 43.05, "longitude": -76.15},   # Syracuse
    "DUNWOD":  {"latitude": 40.93, "longitude": -73.90},   # Yonkers
    "GENESE":  {"latitude": 43.16, "longitude": -77.61},   # Rochester
    "HUD VL":  {"latitude": 41.70, "longitude": -73.93},   # Poughkeepsie
    "LONGIL":  {"latitude": 40.79, "longitude": -73.10},   # Long Island
    "MHK VL":  {"latitude": 41.50, "longitude": -74.01},   # Newburgh
    "MILLWD":  {"latitude": 41.20, "longitude": -73.83},   # Millwood
    "N.Y.C.":  {"latitude": 40.71, "longitude": -74.01},   # New York City
    "NORTH":   {"latitude": 44.70, "longitude": -73.45},   # Plattsburgh
    "WEST":    {"latitude": 42.89, "longitude": -78.88},   # Buffalo
}

# Set up cached session to avoid hammering the API
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=3, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


def fetch_weather():
    latitudes = [z["latitude"] for z in NYISO_ZONES.values()]
    longitudes = [z["longitude"] for z in NYISO_ZONES.values()]
    zone_names = list(NYISO_ZONES.keys())

    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "current": ["temperature_2m", "wind_speed_10m", "cloud_cover"],
    }

    try:
        responses = openmeteo.weather_api(
            "https://api.open-meteo.com/v1/forecast", params=params
        )
    except Exception as e:
        print(f"Failed to fetch weather data: {e}")
        return

    rows = []
    now = datetime.now(timezone.utc)

    for i, response in enumerate(responses):
        current = response.Current()
        rows.append({
            "timestamp": now,
            "zone": zone_names[i],
            "latitude": latitudes[i],
            "longitude": longitudes[i],
            "temperature": current.Variables(0).Value(),   # temperature_2m
            "wind_speed": current.Variables(1).Value(),     # wind_speed_10m
            "cloud_cover": current.Variables(2).Value(),    # cloud_cover
        })

    df = pd.DataFrame(rows)

    with engine.begin() as connection:
        df.to_sql("weather", con=connection, if_exists="append", index=False)

    print(f"Inserted {len(rows)} weather records at {now.isoformat()}")


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=fetch_weather,
        trigger="interval",
        minutes=15,
    )
    fetch_weather()  # run once immediately
    scheduler.start()
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
