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
