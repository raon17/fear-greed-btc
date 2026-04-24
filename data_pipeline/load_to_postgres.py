import psycopg2
from fetch_fng import fetch_fng
from fetch_btc_price import fetch_btc

DB_URL = ""

def load_data():
    df_fng = fetch_fng()
    df_btc = fetch_btc()

    df = df_fng.merge(df_btc, on="date", how="left")

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()


if __name__ == "__main__":
    load_data()
    print("✅ Data loaded successfully")