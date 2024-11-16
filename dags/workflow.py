from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_SCRIPT = os.path.join(BASE_DIR, "result.py")
PUSH_TO_HDFS_SCRIPT = os.path.join(BASE_DIR, "push_to_hdfs.py")

def run_result_script():
    subprocess.run(["python", RESULT_SCRIPT], check=True)

def run_push_to_hdfs_script():
    subprocess.run(["python", PUSH_TO_HDFS_SCRIPT], check=True)

with DAG(
    'data_crawl_and_push_to_hdfs',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Crawl data and push to HDFS',
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    crawl_data = PythonOperator(
        task_id='crawl_data',
        python_callable=run_result_script
    )

    push_to_hdfs = PythonOperator(
        task_id='push_to_hdfs',
        python_callable=run_push_to_hdfs_script
    )

    crawl_data >> push_to_hdfs
