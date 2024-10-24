from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from getData import run_scraping

with DAG(
    dag_id="data_scraping_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="*/20 * * * *",  # Run every 20 minutes
    catchup=False  # Do not catch up on missed runs
) as dag:
    # Define the scraping task
    scrape_data_task = PythonOperator(
        task_id="scrape_data",
        python_callable=run_scraping,  # Call the scraping function
    )

    scrape_data_task