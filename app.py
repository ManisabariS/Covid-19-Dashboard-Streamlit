import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="COVID Dashboard", layout="wide")

st.title("🌍 Real-Time COVID-19 Dashboard")

# ----------- Sidebar -----------

refresh_rate = st.sidebar.slider("Refresh interval (seconds)", 10, 120, 30)

# ----------- API Function -----------

@st.cache_data(ttl=30)
def get_data():
    url = "https://disease.sh/v3/covid-19/countries"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            st.error(f"API Error: {response.status_code}")
            return pd.DataFrame()

        data = response.json()

        df = pd.DataFrame(data)

        return df

    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# ----------- Load Data -----------

df = get_data()

if df.empty:
    st.warning("⚠️ No data available. Try again later.")
    st.stop()

# ----------- Sidebar Filter -----------

country = st.sidebar.selectbox(
    "Select Country",
    df["country"].sort_values().unique()
)

filtered_df = df[df["country"] == country]

# ----------- KPIs -----------

total_cases = int(filtered_df["cases"].values[0])
today_cases = int(filtered_df["todayCases"].values[0])
total_deaths = int(filtered_df["deaths"].values[0])

col1, col2, col3 = st.columns(3)

col1.metric("🦠 Total Cases", f"{total_cases:,}")
col2.metric("📈 Today Cases", f"{today_cases:,}")
col3.metric("💀 Total Deaths", f"{total_deaths:,}")

st.divider()

# ----------- Chart -----------

st.subheader("Top 10 Countries by Cases")

top10 = df.sort_values(by="cases", ascending=False).head(10)

fig, ax = plt.subplots()
ax.bar(top10["country"], top10["cases"])
ax.set_xticklabels(top10["country"], rotation=45)
ax.set_ylabel("Cases")
st.pyplot(fig)

# ----------- Table -----------

st.subheader("📊 Full Data")
st.dataframe(df[["country", "cases", "deaths", "recovered"]])

# ----------- Download -----------

csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    "Download Data",
    csv,
    "covid_data.csv",
    "text/csv"
)

# ----------- Auto Refresh -----------

st.caption(f"Last updated: {time.strftime('%H:%M:%S')}")

time.sleep(refresh_rate)
st.rerun()