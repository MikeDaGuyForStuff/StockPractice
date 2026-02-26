import streamlit as st
import pandas as pd
import sqlite3
import os
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
DB_PATH = "/data/trading_data.db" if os.path.exists("/data") else "trading_data.db"

st.set_page_config(page_title="Crypto Bot Live", layout="wide")
st_autorefresh(interval=10000, key="datarefresh") # Refresh page every 10s

st.title("🤖 Trading Bot Command Center")

def get_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM trades", conn)
    conn.close()
    return df

df = get_data()

if not df.empty:
    # Logic to calculate stats
    total_profit = df['profit'].sum()
    trade_count = len(df)
    
    # Dashboard Layout
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Profit", f"{total_profit:.2f}%")
    col2.metric("Total Trades", trade_count)
    col3.metric("Status", "Running 24/7", "Active")

    # Profit Chart
    st.subheader("Profit Over Time")
    df['cumulative'] = df['profit'].cumsum()
    st.line_chart(df.set_index('timestamp')['cumulative'])

    # Recent Trades Table
    st.subheader("Recent Activity")
    st.dataframe(df.sort_values(by='timestamp', ascending=False), use_container_width=True)
else:
    st.warning("No trades found yet. The bot is likely still waiting for a breakout.")
    st.info(f"Database Path: {DB_PATH}")