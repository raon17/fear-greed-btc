import pandas as pd
import os
from src.fetch import fetch_fear_greed, fetch_btc_price

# Path where the merged CSV gets saved
DATA_PATH = "data/fear_greed_btc.csv"

def add_zones(df):
    bins   = [0, 25, 45, 56, 75, 101]
    labels = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
    df["zone"] = pd.cut(df["value"], bins=bins, labels=labels, right=False)
 
    return df

def add_forward_returns(df):
    for days in [7, 14, 30]:
        df[f"fwd_{days}d_pct"] = (
            df["btc_close"].shift(-days) / df["btc_close"] - 1
        ) * 100

    return df

def load_data(refresh=False):
    if not refresh and os.path.exists(DATA_PATH):
        print(f"Loading merged data from {DATA_PATH}...")
        df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    else:
        print("Fetching fresh data...")
        fg = fetch_fear_greed()
        btc = fetch_btc_price()

        print("Merging datasets...")
        df = pd.merge(fg, btc, on="date", how="inner")

        print("Adding zones and forward returns...")
        df = add_zones(df)
        df = add_forward_returns(df)

        print(f"Saving merged data to {DATA_PATH}...")
        df.to_csv(DATA_PATH, index=False)

    return df