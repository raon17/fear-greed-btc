import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text
from db import get_db_url

st.set_page_config(page_title="BTC Fear & Greed", layout="wide")

@st.cache_data(ttl=3600) # (cached for 1 hour)
def load_data():
    try:
        engine = create_engine(get_db_url())

        with engine.connect() as conn:
            df = pd.read_sql(text(
                    "SELECT * " \
                    "FROM btc_fear_grid " \
                    "ORDER BY date"),
                conn)

        df["date"] = pd.to_datetime(df["date"])
        return df
    
    except Exception as e:
        st.warning(f"DB unavailable - fetching live data ({e})")

        from fetch_btc_price import fetch_btc_price
        from fetch_fng import fetch_fng

        df = pd.merge(fetch_btc_price(90), fetch_fng(90), on="date", how="inner")
        df["date"] = pd.to_datetime(df["date"])

        return df

# Load data ----------------------------------------------------------------
df     = load_data()
latest = df.iloc[-1]
prev   = df.iloc[-2]

# Header -------------------------------------------------------------------
st.title("BTC × Fear & Greed")
st.caption(f"Updated: {latest['date'].strftime('%Y-%m-%d')} · 90-day view")
 
if st.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()
 
st.divider()


 # Metrics -------------------------------------------------------------------

c1, c2, c3 = st.columns(3)
c1.metric("BTC Price", f"${latest['close']:,.0f}", f"${latest['close'] - prev['close']:+,.0f}")
c2.metric("30d High", f"${df.tail(30)['high'].max():,.0f}")
c3.metric("Fear & Greed", f"{int(latest['fng_value'])} — {latest['fng_label']}")

st.divider()