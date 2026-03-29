"""Worker process: runs all data pipelines on a schedule."""
from data.nysio import fetch_price, fetch_load
from data.weather import fetch_weather
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

scheduler.add_job(fetch_price, trigger='interval', seconds=30)
scheduler.add_job(fetch_load, trigger='interval', seconds=30)
scheduler.add_job(fetch_weather, trigger='interval', minutes=15)

# Run once at startup
fetch_weather()

print("Worker started. Scheduling active.")
scheduler.start()
