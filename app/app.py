import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import os

# CONFIG
st.set_page_config(page_title="IMDb 2024 Dashboard", layout="wide", page_icon="🎬")

# LOAD DATA
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(BASE_DIR, "data", "cleaned", "clean_movies.csv")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(path)
    data["Ratings"] = pd.to_numeric(data["Ratings"], errors="coerce")
    data["Votes"] = pd.to_numeric(data["Votes"], errors="coerce").fillna(0).astype(int)
    data["Duration"] = pd.to_numeric(data["Duration"], errors="coerce")
    data["Genre"] = data["Genre"].fillna("Unknown").str.strip()
    data["Duration_hrs"] = data["Duration"] / 60
    return data

if not os.path.exists(CLEAN_PATH):
    st.error("❌ Data file not found. Run scraper → clean → db_upload first.")
    st.stop()

df = load_data(CLEAN_PATH)

# HEADER
st.title("🎬 IMDb 2024 Analytics Dashboard")
st.markdown("Interactive movie insights with filtering and visualization")
st.markdown("---")

# KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("🎬 Total Movies", len(df))
k2.metric("⭐ Avg Rating", f"{df['Ratings'].mean():.2f}")
k3.metric("👍 Total Votes", f"{int(df['Votes'].sum()):,}")
k4.metric("⏱ Avg Duration", f"{df['Duration'].mean():.0f} min")

st.markdown("---")

# SIDEBAR FILTERS
st.sidebar.title("🎛 Filters")

min_rating = st.sidebar.slider("⭐ Min Rating", 0.0, 10.0, 0.0, step=0.1)
min_votes = st.sidebar.number_input("👍 Min Votes", 0, int(df["Votes"].max()), 0)

duration_option = st.sidebar.selectbox(
    "⏱ Duration",
    ["All", "< 2 hrs", "2 - 3 hrs", "> 3 hrs"]
)

genres = sorted(df["Genre"].unique())
selected_genre = st.sidebar.multiselect("🎭 Genre", genres)

# APPLY FILTERS
filtered = df.copy()
filtered = filtered[filtered["Ratings"] >= min_rating]
filtered = filtered[filtered["Votes"] >= min_votes]

if duration_option == "< 2 hrs":
    filtered = filtered[filtered["Duration"] < 120]
elif duration_option == "2 - 3 hrs":
    filtered = filtered[(filtered["Duration"] >= 120) & (filtered["Duration"] <= 180)]
elif duration_option == "> 3 hrs":
    filtered = filtered[filtered["Duration"] > 180]

if selected_genre:
    filtered = filtered[filtered["Genre"].isin(selected_genre)]

# TABLE
st.subheader("📋 Filtered Dataset")
st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

st.markdown("---")

def show(fig):
    st.pyplot(fig)
    plt.close()

# TOP RATED
st.subheader("🏆 Top 10 by Rating")
top10 = df.sort_values("Ratings", ascending=False).head(10)
st.dataframe(top10, use_container_width=True)

# GENRE DISTRIBUTION
st.subheader("🎭 Genre Distribution")
if df["Genre"].nunique() > 1:
    counts = df["Genre"].value_counts().head(15)
    fig, ax = plt.subplots()
    ax.bar(counts.index, counts.values)
    plt.xticks(rotation=45)
    show(fig)
else:
    st.warning("Not enough genre variety")

# RATING DISTRIBUTION
st.subheader("⭐ Rating Distribution")
fig, ax = plt.subplots()
sns.histplot(df["Ratings"].dropna(), bins=10, kde=True, ax=ax)
show(fig)

# VOTES VS RATING
st.subheader("🔗 Ratings vs Votes")
fig, ax = plt.subplots()
sns.scatterplot(data=df, x="Votes", y="Ratings", ax=ax)
show(fig)

st.markdown("---")
st.markdown("🚀 Built with Streamlit")

