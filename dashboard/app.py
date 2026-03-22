
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Add parent directory to path so we can import from src/

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.fetch     import fetch_fear_greed
from src.transform import load_data
from src.backtest  import (
    zone_stats,
    threshold_backtest,
    significance_test,
    sweep_thresholds,
)

# Streamlit page config
st.set_page_config(
    page_title="Fear & Greed Backtest",
    layout="wide",
)

st.title("Crypto Fear & Greed Index — Backtest Dashboard")
st.caption("Backtesting the Fear & Greed Index as a BTC buy signal against buy-and-hold.")

today = fetch_fear_greed(limit=1).iloc[0] # Fetch just today's single reading to show at the top

c1, c2, c3, c4 = st.columns(4)
c1.metric("Today's index",  int(today["value"]))
c2.metric("Zone",           today["value_classification"])
c3.metric("Interpretation", "Buy signal" if int(today["value"]) < 25 else
                             "Watch"      if int(today["value"]) < 45 else
                             "Neutral"    if int(today["value"]) < 56 else
                             "Caution"    if int(today["value"]) < 75 else
                             "Sell signal")
c4.metric("Scale", "0 = Max Fear  |  100 = Max Greed")


# Controls 
st.divider()
st.subheader("Backtest settings")

col_a, col_b = st.columns(2)

horizon = col_a.select_slider(
    options=[7, 14, 30],
    value=30,
    help="How many days after the signal do we measure the BTC return?",
)

threshold = col_b.slider(
    min_value=10,
    max_value=40,
    value=25,
    step=5,
    help="Lower = only buy in deep fear. Higher = buy in mild fear too.",
)

# Load data and run analysis 
df     = load_data()
stats  = zone_stats(df, horizon=horizon)
result = threshold_backtest(df, threshold=threshold, horizon=horizon)
sig    = significance_test(df, threshold=threshold, horizon=horizon)


# Summary metrics 
st.divider()
st.subheader("Signal vs buy-and-hold")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Signal trades",      result["signal_trades"],
          help="Number of days the buy signal triggered")
m2.metric("Signal avg return",  f"{result['signal_avg_return']}%",
          delta=f"{round(result['signal_avg_return'] - result['bah_avg_return'], 2)}% vs B&H")
m3.metric("Signal win rate",    f"{result['signal_win_rate']}%",
          delta=f"{round(result['signal_win_rate'] - result['bah_win_rate'], 1)}% vs B&H")
m4.metric("B&H avg return",     f"{result['bah_avg_return']}%",
          help="Buy-and-hold benchmark -- holds BTC every day")

# Statistical significance result
sig_text  = "Statistically significant at 5% level" if sig["significant"] else "Not statistically significant — could be noise"
sig_icon  = "success" if sig["significant"] else "warning"

if sig["significant"]:
    st.success(f"t = {sig['t_stat']}  |  p = {sig['p_value']}  →  {sig_text}  (n_fear={sig['fear_n']}, n_other={sig['other_n']})")
else:
    st.warning(f"t = {sig['t_stat']}  |  p = {sig['p_value']}  →  {sig_text}  (n_fear={sig['fear_n']}, n_other={sig['other_n']})")

#  Zone colours  used across all charts for consistency and easier interpretation
zone_colors = {
    "Extreme Fear":  "#E24B4A",
    "Fear":          "#EF9F27",
    "Neutral":       "#888780",
    "Greed":         "#639922",
    "Extreme Greed": "#0f6e56",
}


# Chart 1: Average return by zone 
st.divider()
st.subheader(f"Average {horizon}-day return by zone")

fig1 = px.bar(
    stats,
    x="zone",
    y="avg_return",
    color="zone",
    color_discrete_map=zone_colors,
    text="avg_return",
    labels={"avg_return": "Avg return %", "zone": ""},
)
fig1.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig1.update_layout(showlegend=False, height=340, yaxis_title="Avg return %")
fig1.add_hline(y=0, line_color="gray", line_width=0.8)
st.plotly_chart(fig1, use_container_width=True)
