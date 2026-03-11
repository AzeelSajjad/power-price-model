from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

#loading environment variables
load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_PORT = 5432
DB_HOST = 'localhost'

database_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

#create the sqlalchemy engine
engine = create_engine(database_url)

try:
    #use engine.connect() to connect the database and if it connects succesfully print statement will show
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")