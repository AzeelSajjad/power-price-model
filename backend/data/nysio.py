import pandas as pd
import requests
from db import engine
import io
from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime

def fetch_price():
    date = datetime.now().strftime('%Y%m%d')
    url = f"https://mis.nyiso.com/public/csv/rtlbmp/{date}rtlbmp_zone.csv"
    response = requests.get(url)
    if response.status_code == 200:
        print("Reached page")
        with engine.begin() as connection:
            df = pd.read_csv(io.StringIO(response.text))
            df.to_sql('prices', con=connection, if_exists='append', index=False)
    else:
        print(f"Failed to reach page. Status code: {response.status_code}")
        
def fetch_load():
    date = datetime.now().strftime('%Y%m%d')
    url = f"https://mis.nyiso.com/public/csv/pal/{date}pal.csv"
    response = requests.get(url)
    if response.status_code == 200:
        print("Reached page")
        with engine.begin() as connection:
            df = pd.read_csv(io.StringIO(response.text))
            df.to_sql('load', con=connection, if_exists='append', index=False)
    else:
        print(f"Failed to reach page. Status code: {response.status_code}")
        
if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=fetch_price,
        trigger='interval',
        hours=1
    )
    scheduler.add_job(
        func=fetch_load,
        trigger='interval',
        hours=1
    )
    scheduler.start()
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
    