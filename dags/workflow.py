from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
import os

# Đường dẫn các script

os.environ['JAVA_HOME'] = '/opt/jdk'
os.environ['LD_LIBRARY_PATH'] = '/opt/jdk/jre/lib/amd64/server'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_SCRIPT = os.path.join(BASE_DIR, "result.py")
PUSH_TO_HDFS_SCRIPT = os.path.join(BASE_DIR, "push_to_hdfs.py")
MIGRATE_HDFS_TO_POSTGRES_SCRIPT = os.path.join(BASE_DIR, "migrate_hdfs_to_postgres.py")

def run_script(script_path):
    """
    Chạy một script Python cụ thể và kiểm tra lỗi.
    """
    import os
    os.environ["JAVA_HOME"] = "/opt/jdk"
    os.environ["LD_LIBRARY_PATH"] = "/opt/jdk/jre/lib/amd64/server:" + os.environ.get("LD_LIBRARY_PATH", "")
    
    try:
        subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Lỗi khi chạy script {script_path}: {e}")


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
    start_date=datetime(2024, 11, 19),
    catchup=False,
) as dag:

    crawl_data = PythonOperator(
        task_id='crawl_data',
        python_callable=run_script,
        op_args=[RESULT_SCRIPT],  # Truyền đường dẫn script "result.py"
    )

    push_to_hdfs = PythonOperator(
        task_id='push_to_hdfs',
        python_callable=run_script,
        op_args=[PUSH_TO_HDFS_SCRIPT],  # Truyền đường dẫn script "push_to_hdfs.py"
    )

    migrate_hdfs_to_postgres = PythonOperator(
        task_id='migrate_hdfs_to_postgres',
        python_callable=run_script,
        op_args=[MIGRATE_HDFS_TO_POSTGRES_SCRIPT],  # Truyền đường dẫn script "migrate_hdfs_to_postgres.py"
    )


    # crawl_data 
    push_to_hdfs
    # migrate_hdfs_to_postgres
    
    
