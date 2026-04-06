import sys
import os
sys.path.insert(0, '/opt/airflow/src')

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from fetch import fetch_articles
from extract import process_articles
from store import store_articles

def task_fetch(**context):
    articles = fetch_articles(topic="artificial intelligence", page_size=20)
    context["ti"].xcom_push(key="raw_articles", value=articles)
    print(f"Fetched {len(articles)} articles")

def task_extract(**context):
    articles = context["ti"].xcom_pull(key="raw_articles", task_ids="fetch_articles")
    enriched = process_articles(articles)
    context["ti"].xcom_push(key="enriched_articles", value=enriched)
    print(f"Extracted insights for {len(enriched)} articles")

def task_store(**context):
    articles = context["ti"].xcom_pull(key="enriched_articles", task_ids="llm_extract")
    store_articles(articles)

def task_notify(**context):
    articles = context["ti"].xcom_pull(key="enriched_articles", task_ids="llm_extract")
    print(f"Pipeline complete. Processed {len(articles)} articles.")

default_args = {
    "owner": "you",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False
}

with DAG(
    dag_id="news_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule="0 8 * * *",
    catchup=False,
    tags=["nlp", "llm", "news"]
) as dag:

    fetch   = PythonOperator(task_id="fetch_articles", python_callable=task_fetch)
    extract = PythonOperator(task_id="llm_extract",    python_callable=task_extract)
    store   = PythonOperator(task_id="store_results",  python_callable=task_store)
    notify  = PythonOperator(task_id="notify",         python_callable=task_notify)

    fetch >> extract >> store >> notify