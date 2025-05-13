from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_local import GCSToLocalFilesystemOperator
from airflow.providers.google.cloud.operators.gcs import GCSListObjectsOperator
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from datetime import datetime, timedelta
import os

# Ensure tmp directory exists
os.makedirs('/tmp', exist_ok=True)

# Move heavy imports inside the function to improve DAG load time
def load_to_sql(file_path):
    import pandas as pd
    import sqlalchemy
    
    conn = BaseHook.get_connection('postgres_default')  
    engine = sqlalchemy.create_engine(
        f"postgresql+psycopg2://{conn.login}:{conn.password}@mlops-third-project_c9680c-postgres-1:{conn.port}/{conn.schema}"
    )
    df = pd.read_csv(file_path)
    df.to_sql(
        name="titanic",
        con=engine,
        if_exists="replace",
        index=False
    )

# DAG definition
dag = DAG(
    dag_id="extract_titanic_data",
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    schedule="@once",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['titanic', 'gcp'],
    description='Extract Titanic data from GCS and load to PostgreSQL',
)

# Task definitions
list_files = GCSListObjectsOperator(
    task_id="list_files",
    bucket="bucket-mlop-001",
    delimiter='.csv',
    dag=dag,
)

download_file = GCSToLocalFilesystemOperator(
    task_id="download_file",
    bucket="bucket-mlop-001",
    object_name="Titanic-Dataset.csv",
    filename="/tmp/Titanic-Dataset.csv",
    dag=dag,
)

load_data = PythonOperator(
    task_id="load_to_sql",
    python_callable=load_to_sql,
    op_kwargs={"file_path": "/tmp/Titanic-Dataset.csv"},
    dag=dag,
)

# Task dependencies
list_files >> download_file >> load_data
