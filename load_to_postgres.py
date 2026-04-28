import psycopg2 
import pandas as pd
from sqlalchemy import create_engine 
from fetch_btc_price import fetch_btc_price
from fetch_fng import fetch_fng
from db import DB_CONFIG, get_db_url 

TABLE_NAME = "btc_fear_grid"

def get_engine():
    return create_engine(get_db_url())


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
   