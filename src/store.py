from sqlalchemy import create_engine
import pandas as pd
import os

DB_PATH = "/opt/airflow/data/news.db"

def store_articles(articles: list) -> None:
    os.makedirs("/opt/airflow/data", exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}")

    df = pd.DataFrame(articles)

    # Convert list columns to strings for SQLite
    df["topics"] = df["topics"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else str(x)
    )
    df["key_entities"] = df["key_entities"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else str(x)
    ) if "key_entities" in df.columns else ""

    df["ingested_at"] = pd.Timestamp.now()

    df.to_sql("articles", engine, if_exists="append", index=False)
    print(f"Stored {len(df)} articles to database")