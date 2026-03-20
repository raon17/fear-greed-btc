import pandas as pd
import os
from src.fetch import fetch_fear_greed, fetch_btc_price

# Path where the merged CSV gets saved
DATA_PATH = "data/fear_greed_btc.csv"

def add_zones(df):

    # Add a 'zone' column that labels each day by its Fear & Greed range.
    bins   = [0, 25, 45, 56, 75, 101]
    labels = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
    df["zone"] = pd.cut(df["value"], bins=bins, labels=labels, right=False) # right=False to include [75,101) in Extreme Greed
    return df

def add_forward_returns(df):
    # Calculate forward returns for 7, 14, and 30 day horizons
    for days in [7, 14, 30]:
        # shift(-days) moves the btc_close column up by 'days' rows, so we get the future price
        #(future price / current price - 1) * 100 gives the percentage return
        # Core idea: if I bought on day 0 at price P0, and sold on day N at price PN, my return is (PN / P0 - 1) * 100
        df[f"fwd_{days}d_pct"] = (df["btc_close"].shift(-days) / df["btc_close"] - 1) * 100
    return df


def load_data(refresh=False):
    # If cache exists and we don't want a refresh, just load it
    if not refresh and os.path.exists(DATA_PATH):
        print(f"Loading from cache: {DATA_PATH}")
        return pd.read_csv(DATA_PATH, parse_dates=["date"])

    # Otherwise fetch fresh data from both APIs
    print("Fetching Fear & Greed data...")
    fg = fetch_fear_greed(limit=2000)
    print("Fetching BTC price data...")
    btc = fetch_btc_price()

    # Merge on date, where inner join keeps only rows where both have data
    print("Merging datasets...")
    df = pd.merge(fg, btc, on="date", how="inner")

    # Drop any rows with missing values
    df = df.dropna(subset=["btc_close"])

    # Add zone labels and forward returns
    df = add_zones(df)
    df = add_forward_returns(df) # This creates new columns fwd_7d_pct, fwd_14d_pct, fwd_30d_pct with the future returns for each horizon

    # Reset index after dropping rows to keep it clean
    df = df.reset_index(drop=True)

    # Save to CSV for next time
    os.makedirs("data", exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"Saved {len(df)} rows to {DATA_PATH}")

    return df

# Quick test - load the data and print some info about it
if __name__ == "__main__":
    df = load_data(refresh=True)

    print(f"\nShape: {df.shape}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nDate range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"\nZone counts:\n{df['zone'].value_counts()}")
    print(f"\nFirst 5 rows:\n{df.head()}")
    print(f"\nLast 5 rows (fwd returns will be NaN):\n{df.tail()}")