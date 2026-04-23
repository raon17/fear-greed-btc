import requests 
import pandas as pd 

def fetch_fng(limit=90):
    url = f"https://api.alternative.me/fng/?limit={limit}&format=json"
    data = requests.get(url).json()["data"]

    df = pd.DataFrame(data)
    df["value"] = df["value"].astype(int)
    df["date"] = pd.to_datetime(df["timestamp"].astype(int), unit="s").dt.date
    df = df.sort_values("date")

    df["sentiment"] = df["value"].apply(classify)

    return df[["date", "value", "sentiment"]]

def classify(v):
    if v <= 24: return "Extreme Fear"
    if v <= 44: return "Fear"
    if v <= 54: return "Neutral"
    if v <= 74: return "Greed"
    return "Extreme Greed"

def test():
    df = fetch_fng()
    print(df)

if __name__ == "__main__":
    test()