import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text
from db import get_db_url

st.set_page_config(page_title="BTC Fear & Greed", layout="wide")


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
