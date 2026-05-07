"""
fetch.py  —  BTC price + Fear & Greed Index
"""

import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta

FNG_URL = "https://api.alternative.me/fng/"


def fetch_btc(days: int = 90) -> pd.DataFrame:
    end   = datetime.today()
    start = end - timedelta(days=days)

    df = yf.Ticker("BTC-USD").history(
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        interval="1d",
    )
    df = df.reset_index()
    df.columns = [c.lower() for c in df.columns]
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df[["date", "open", "high", "low", "close", "volume"]].dropna()


def fetch_fng(days: int = 90) -> pd.DataFrame:
    data = requests.get(FNG_URL, params={"limit": days}, timeout=10).json()["data"]
    df = pd.DataFrame([{
        "date":      datetime.fromtimestamp(int(e["timestamp"])).date(),
        "fng_value": int(e["value"]),
        "fng_label": e["value_classification"],
    } for e in data])
    return df.sort_values("date").reset_index(drop=True)


def fetch_merged(days: int = 90) -> pd.DataFrame:
    """Fetch both sources and inner-join on date."""
    return pd.merge(fetch_btc(days), fetch_fng(days), on="date", how="inner")