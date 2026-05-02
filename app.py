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


# helpers
 
def fng_gradient_color(v: int) -> str:
    v = max(0, min(100, v))
    if v <= 50:
        t = v / 50     
        r = int(220 + t * (240 - 220))   
        g = int(50  + t * (200 - 50))      
        b = int(50  + t * (50  - 50))      
    else:
        t = (v - 50) / 50              
        r = int(240 + t * (50  - 240))    
        g = int(200 + t * (200 - 200)) 
        b = int(50  + t * (100 - 50))  
    return f"#{r:02x}{g:02x}{b:02x}"
  
#  layout
 
chart_col, gauge_col = st.columns([3, 1])
 
with chart_col:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.65, 0.35],
        vertical_spacing=0.04,
    )
 
    # BTC price line (top)
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["close"],
        mode="lines", name="BTC/USD",
        line=dict(color="#ffffff", width=2),
    ), row=1, col=1)
 
    # F&G gradient bars (bottom)
    fig.add_trace(go.Bar(
        x=df["date"], y=df["fng_value"],
        name="Fear & Greed",
        marker_color=[fng_gradient_color(v) for v in df["fng_value"]],
        hovertemplate="%{x|%Y-%m-%d}<br>F&G: %{y}<extra></extra>",
    ), row=2, col=1)
 
    # zone reference lines
    for level, label in [(25, "Fear"), (50, "Neutral"), (75, "Greed")]:
        fig.add_hline(y=level, line_dash="dot",
                      line_color="rgba(255,255,255,0.12)",
                      annotation_text=label, annotation_position="right",
                      row=2, col=1)
 
    fig.update_layout(
        height=520, template="plotly_dark",
        showlegend=False,
        margin=dict(l=10, r=80, t=10, b=10),
    )
    fig.update_yaxes(title_text="USD", row=1, col=1)
    fig.update_yaxes(title_text="F&G", row=2, col=1, range=[0, 100])
    fig.update_xaxes(rangeslider_visible=False)
 
    st.plotly_chart(fig, use_container_width=True)
 
with gauge_col:
    fng_val   = int(latest["fng_value"])
    fng_label = latest["fng_label"]
 
    # Plotly gauge chart
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fng_val,
        title=dict(text=f"<b>{fng_label}</b>", font=dict(size=14)),
        number=dict(font=dict(size=36, color=fng_gradient_color(fng_val))),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["0", "25", "50", "75", "100"],
                tickfont=dict(size=10),
            ),
            bar=dict(color=fng_gradient_color(fng_val), thickness=0.25),
            steps=[
                dict(range=[0,  25], color="rgba(220,50,50,0.25)"),
                dict(range=[25, 45], color="rgba(230,120,30,0.2)"),
                dict(range=[45, 55], color="rgba(240,200,50,0.2)"),
                dict(range=[55, 75], color="rgba(80,190,80,0.2)"),
                dict(range=[75,100], color="rgba(50,180,90,0.25)"),
            ],
            threshold=dict(
                line=dict(color="white", width=2),
                thickness=0.75,
                value=fng_val,
            ),
        ),
    ))
 
    gauge.update_layout(
        height=300,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
    )
 
    st.plotly_chart(gauge, use_container_width=True)
 
    # zone legend under gauge
    st.markdown("""
    <div style="font-size:12px; line-height:2; margin-top:-10px">
        <span style="color:#dc3232">█</span> 0–25 &nbsp; Extreme Fear<br>
        <span style="color:#e67e22">█</span> 26–45 &nbsp; Fear<br>
        <span style="color:#f0c832">█</span> 46–55 &nbsp; Neutral<br>
        <span style="color:#50be50">█</span> 56–75 &nbsp; Greed<br>
        <span style="color:#32b464">█</span> 76–100 &nbsp; Extreme Greed
    </div>
    """, unsafe_allow_html=True)
 
# fear grid table 
 
st.subheader("Last 14 Days")
 
grid = (df.tail(14)[["date", "close", "fng_value", "fng_label"]]
          .copy()
          .iloc[::-1]
          .reset_index(drop=True))
grid["date"]  = grid["date"].dt.strftime("%Y-%m-%d")
grid["close"] = grid["close"].apply(lambda x: f"${x:,.0f}")
grid.columns  = ["Date", "BTC Close", "F&G Score", "Sentiment"]
 
st.dataframe(grid, use_container_width=True, hide_index=True)
 