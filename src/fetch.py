import requests
import pandas as pd
import yfinance as yf

# Fear & Greed Index #
def fetch_fear_greed(limit=1000):
    url = f"https://api.alternative.me/fng/?limit={limit}&format=json"

    response = requests.get(url, timeout=10)
    response.raise_for_status()          

    data = response.json()["data"]       
    df = pd.DataFrame(data)

    # API timestamps as strings of Unix seconds and convert to datetime format
    df["date"] = pd.to_datetime(df["timestamp"].astype(int), unit="s")

    # API string convert to integer
    df["value"] = df["value"].astype(int)

    df = df[["date", "value", "value_classification"]]

    # Sort by date (oldest to newest) and reset index
    df = df.sort_values("date").reset_index(drop=True)

    return df

# BTC Price History 

def fetch_btc_price(start="2018-02-01"):

    df = yf.download("BTC-USD", start=start, progress=False)

    df = df[["Close"]].reset_index()
    df.columns = ["date", "btc_close"]

    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)

    df = df.reset_index(drop=True)

    return df

# Quick test 
if __name__ == "__main__":
    print("Fetching Fear & Greed (last 5 days)...")
    fg = fetch_fear_greed(limit=5)
    print(fg)
    print(f"\nShape: {fg.shape}")
    print(f"Dtypes:\n{fg.dtypes}")

    print("\nFetching BTC price (last 5 rows)...")
    btc = fetch_btc_price()
    print(btc.tail())
    print(f"\nShape: {btc.shape}")
    print(f"Dtypes:\n{btc.dtypes}")

    print("\nBoth fetched successfully")