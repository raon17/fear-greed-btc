import requests
import pandas as pd
import yfinance as yf


def fetch_fear_greed(limit=1000):
    url = f"https://api.alternative.me/fng/?limit={limit}&format=json"
    response = requests.get(url).json()
    print(response)               # see the full structure
    print(response.keys())        # see top-level keys
    print(type(response["data"]))

fetch_fear_greed()
#     data = requests.get(url, timeout=10).json()["data"]
#     df = pd.DataFrame(data)
#     df["date"]  = pd.to_datetime(df["timestamp"].astype(int), unit="s")
#     df["value"] = df["value"].astype(int)
#     df = df[["date", "value", "value_classification"]]
#     return df.sort_values("date").reset_index(drop=True)

# def fetch_btc_price(start="2018-02-01"):
#     df = yf.download("BTC-USD", start=start, progress=False)
#     df = df[["Close"]].reset_index()
#     df.columns = ["date", "btc_close"]
#     df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
#     return df.reset_index(drop=True)