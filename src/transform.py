import pandas as pd
import os
from src.fetch import fetch_fear_greed, fetch_btc_price

DATA_PATH = "data/fear_greed_btc.csv"

#Bucket boundaries for fear-greed index
def add_zones(df):
    bins   = [0, 25, 45, 56, 75, 101]
    labels = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
    df["zone"] = pd.cut(df["value"], bins=bins, labels=labels, right=False)
    return df