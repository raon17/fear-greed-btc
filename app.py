import streamlit as st       
import pandas as pd
import plotly.graph_objects as go     
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text 
from db import get_db_url  


st.set_page_config(
    page_title="BTC Fear & Greed Dashboard",
    page_icon="₿",
    layout="wide",
)

