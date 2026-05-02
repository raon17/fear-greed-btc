
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
    print(f" Table '{TABLE_NAME}' ready")


def merge_data(days: int = 90):
    btc = fetch_btc_price(days=days)
    fng = fetch_fng(days=days)

    merged = pd.merge(btc, fng, on="date", how="inner")
    print(f" Merged: {len(merged)} rows")
    return merged


def upsert_to_postgres(df: pd.DataFrame):
    engine = get_engine()

    df.to_sql("_staging", engine, if_exists="replace", index=False)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO {TABLE_NAME}
            SELECT * FROM _staging
        ON CONFLICT (date) DO UPDATE SET
            open      = EXCLUDED.open,
            high      = EXCLUDED.high,
            low       = EXCLUDED.low,
            close     = EXCLUDED.close,
            volume    = EXCLUDED.volume,
            fng_value = EXCLUDED.fng_value,
            fng_label = EXCLUDED.fng_label;
        DROP TABLE IF EXISTS _staging;
    """)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(df)} rows into '{TABLE_NAME}'")


def run(days: int = 90):
    create_table_if_not_exists()
    df = merge_data(days=days)
    upsert_to_postgres(df)
    print("Load complete!")


if __name__ == "__main__":
    run(days=90)