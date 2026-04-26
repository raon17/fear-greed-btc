import psycopg2                       
import pandas as pd
from sqlalchemy import create_engine    
from fetch_btc_price import fetch_btc_price
from fetch_fng import fetch_fng
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DB_CONFIG = {
    "host": DB_HOST,
    "port": DB_PORT,
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD
}

TABLE_NAME = "btc_fear_grid"

def get_engine():
    cfg = DB_CONFIG
    url = f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
    return create_engine(url)
 
def create_table_if_not_exists():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            date        DATE PRIMARY KEY,
            open        NUMERIC,
            high        NUMERIC,
            low         NUMERIC,
            close       NUMERIC,
            volume      BIGINT,
            fng_value   SMALLINT,
            fng_label   VARCHAR(20)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Table '{TABLE_NAME}' ready")