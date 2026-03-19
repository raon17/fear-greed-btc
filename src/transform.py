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

    print("Fetching Fear & Greed data...")
    fg = fetch_fear_greed(limit=2000)
 
    print("Fetching BTC price data...")
    btc = fetch_btc_price()
 
    # Merge on date to keeps only rows where both have data. Drop weekends and any API gaps
    print("Merging datasets...")
    df = pd.merge(fg, btc, on="date", how="inner")
 
    df = df.dropna(subset=["btc_close"])
 
    df = add_zones(df)
    df = add_forward_returns(df)
 
    df = df.reset_index(drop=True)

    os.makedirs("data", exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"Saved {len(df)} rows to {DATA_PATH}")
 
    return df

# Quick test
if __name__ == "__main__":
    df = load_data(refresh=True)
 
    print(f"\nShape: {df.shape}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nDate range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"\nZone counts:\n{df['zone'].value_counts()}")
    print(f"\nFirst 5 rows:\n{df.head()}")
    print(f"\nLast 5 rows (fwd returns will be NaN):\n{df.tail()}")