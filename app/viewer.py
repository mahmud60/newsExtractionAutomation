import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

DB_PATH = "/opt/airflow/data/news.db"

@st.cache_data(ttl=300)
def load_data():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    df = pd.read_sql("SELECT * FROM articles ORDER BY ingested_at DESC", engine)
    return df

st.set_page_config(page_title="News Intelligence Dashboard", layout="wide")
st.title("News Intelligence Dashboard")
st.caption("Powered by NewsAPI + Groq + Airflow")

df = load_data()

if df.empty:
    st.warning("No articles found. Run the Airflow pipeline first.")
    st.stop()

# --- Metrics row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Articles", len(df))
col2.metric("Positive", len(df[df["sentiment"] == "positive"]))
col3.metric("Negative", len(df[df["sentiment"] == "negative"]))
col4.metric("Neutral",  len(df[df["sentiment"] == "neutral"]))

st.divider()

# --- Sentiment chart ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Sentiment breakdown")
    sentiment_counts = df["sentiment"].value_counts()
    st.bar_chart(sentiment_counts)

with col_right:
    st.subheader("Top sources")
    source_counts = df["source"].value_counts().head(8)
    st.bar_chart(source_counts)

st.divider()

# --- Filters ---
st.subheader("Browse articles")
col_f1, col_f2 = st.columns(2)

with col_f1:
    sentiment_filter = st.selectbox(
        "Filter by sentiment",
        ["All", "positive", "negative", "neutral"]
    )

with col_f2:
    search = st.text_input("Search by keyword")

filtered = df.copy()
if sentiment_filter != "All":
    filtered = filtered[filtered["sentiment"] == sentiment_filter]
if search:
    filtered = filtered[
        filtered["title"].str.contains(search, case=False, na=False) |
        filtered["summary"].str.contains(search, case=False, na=False)
    ]

st.caption(f"Showing {len(filtered)} articles")

# --- Article cards ---
for _, row in filtered.iterrows():
    with st.expander(f"**{row['title']}** — {row['source']}"):
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.write(row["summary"])
            st.caption(f"Topics: {row['topics']}")
            st.caption(f"Key entities: {row.get('key_entities', '')}")
        with col_b:
            sentiment = row["sentiment"]
            color = {"positive": "green", "negative": "red", "neutral": "gray"}.get(sentiment, "gray")
            st.markdown(f":{color}[{sentiment.upper()}]")
            st.caption(row["published_at"][:10])
            st.link_button("Read full article", row["url"])