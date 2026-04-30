import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def fetch_btc_price(days: int = 90):
    end = datetime.today()
    start = end - timedelta(days=days)
    ticker = yf.Ticker("BTC-USD")
    df = ticker.history(start=start.strftime("%Y-%m-%d"),
                        end=end.strftime("%Y-%m-%d"),
                        interval="1d")
    df = df.reset_index()
    df.columns = [c.lower() for c in df.columns]
    df = df.rename(columns={"date": "date"})
    df["date"] = pd.to_datetime(df["date"]).dt.date 
    df = df[["date", "open", "high", "low", "close", "volume"]]
    df = df.dropna()

    print(f"BTC price: {len(df)} rows fetched ({df['date'].min()} -> {df['date'].max()})")
    return df


if __name__ == "__main__":
    df = fetch_btc_price(days=90)
    print(df.tail(3))