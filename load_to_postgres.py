"""
load_to_postgres.py
-------------------
Merges BTC price + Fear & Greed data and upserts into PostgreSQL.

Libraries:
  - psycopg2    : raw postgres connection + table creation
  - sqlalchemy  : DataFrame.to_sql() for easy bulk insert
  - pandas      : merge / transform
"""

import psycopg2                          # pip install psycopg2-binary
import pandas as pd
from sqlalchemy import create_engine     # pip install sqlalchemy
from fetch_btc_price import fetch_btc_price
from fetch_fng import fetch_fng
from db import DB_CONFIG, get_db_url    # ← credentials from .env


TABLE_NAME = "btc_fear_grid"


def get_engine():
    """SQLAlchemy engine for pandas to_sql()."""
    return create_engine(get_db_url())


def create_table_if_not_exists():
    """Create table using raw psycopg2 (DDL)."""
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
    print(f"✅ Table '{TABLE_NAME}' ready")


def merge_data(days: int = 90) -> pd.DataFrame:
    """
    Fetch both sources and inner-join on date.

    BTC:  [date, open, high, low, close, volume]
    F&G:  [date, fng_value, fng_label]
    → merged on date (inner join)
    """
    btc = fetch_btc_price(days=days)
    fng = fetch_fng(days=days)

    # Inner join — only rows where both sources have data
    merged = pd.merge(btc, fng, on="date", how="inner")
    print(f"✅ Merged: {len(merged)} rows")
    return merged


def upsert_to_postgres(df: pd.DataFrame):
    """
    Upsert strategy: delete existing dates then re-insert.
    Simple and reliable for daily batch loads.

    Flow:
      DataFrame → to_sql("temp") → DELETE+INSERT into main table
    """
    engine = get_engine()

    # Write to a temp staging table
    df.to_sql("_staging", engine, if_exists="replace", index=False)

    # Upsert via raw SQL
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
    print(f"✅ Upserted {len(df)} rows into '{TABLE_NAME}'")


def run(days: int = 90):
    create_table_if_not_exists()
    df = merge_data(days=days)
    upsert_to_postgres(df)
    print("🎉 Load complete!")


if __name__ == "__main__":
    run(days=90)