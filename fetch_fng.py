import requests 
import pandas as pd
from datetime import datetime

FNG_URL = "https://api.alternative.me/fng/"

def fetch_fng(days: int = 90):
    params = {"limit": days, "format": "json"}
    response = requests.get(FNG_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()["data"]

    rows = []
    for entry in data:
        rows.append({
            "date": datetime.fromtimestamp(int(entry["timestamp"])).date(),
            "fng_value": int(entry["value"]),
            "fng_label": entry["value_classification"],
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("date").reset_index(drop=True)

    print(f"F&G Index: {len(df)} rows fetched ({df['date'].min()} -> {df['date'].max()})")
    return df


if __name__ == "__main__":
    df = fetch_fng(days=10)
    print(df.tail(5))
