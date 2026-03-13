import pandas as pd
import requests
from models.prices import Price
from models.load import Load
from db import engine
import io

def fetch_price(date):
    date = date.strip('-')
    url = f"https://mis.nyiso.com/public/csv/rtlbmp/{date}rtlbmp_zone.csv"
    response = requests.get(url)
    if response.status_code == 200:
        print("Reached page")
    else:
        print("Failed to reach page. Status code: {response.status_code}")
    with engine.begin() as connection:
        df = pd.read_csv(io.StringIO(response.text))
        df.to_sql('prices', con=connection, if_exists='append', index=False)
        
def fetch_load(date):
    date = date.strip('-')
    url = f"https://mis.nyiso.com/public/csv/pal/{date}pal.csv"
    response = requests.get(url)
    if response.status_code == 200:
        print("Reached page")
    else:
        print("Failed to reach page. Status code: {response.status_code}")
    with engine.begin() as connection:
        df = pd.read_csv(io.StringIO(response.text))
        df.to_sql('load', con=connection, if_exists='append', index=False)