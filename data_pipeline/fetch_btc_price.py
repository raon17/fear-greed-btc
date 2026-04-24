import requests
import pandas as pd

def fetch_btc(days=90):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": days}

    data = requests.get(url, params=params).json()
    prices = data["prices"]

    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date

    df = df.groupby("date")["price"].mean().reset_index()

    return df

def test():
    df = fetch_btc()
    print(df)

if __name__ == "__main__":
    test()