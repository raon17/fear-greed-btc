import requests 
import pandas as pd 
import plotly.graph_objects as go

# Fetch 90 days of Fear & Greed Index data from the API
url = "https://api.alternative.me/fng/?limit=90&format=json"
data = requests.get(url).json()["data"]

# 2. DataFrame으로 변환 
df = pd.DataFrame(data) 
df = pd.DataFrame(data)
df["value"] = df["value"].astype(int) 
df["date"] = pd.to_datetime(df["timestamp"].astype(int), unit="s") 
df = df.sort_values("date")