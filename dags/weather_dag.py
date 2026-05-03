from datetime import datetime, timedelta
from airflow.decorators import dag, task
import sys
import os

sys.path.insert(0, '/opt/airflow/src')

from extract_data import extract_data
from load_data import load_weather_data
from transform_data import data_transformation_pipeline


@dag(
    dag_id='clima_uirauna_etl',
    default_args={
        'owner': 'admin',
        'depends_on_past': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5)
    },
    description='Pipeline ETL - Clima Uiraúna',
    schedule='0 */1 * * *',
    start_date=datetime(2026, 5, 2),
    catchup=False,
    tags=['weather', 'etl']
)
def weather_pipeline():

    @task
    def extract():
        from dotenv import load_dotenv
        load_dotenv('/opt/airflow/config/.env')
        api_key = os.getenv('API_KEY')
        if not api_key:
            raise ValueError("API_KEY não encontrada no .env")
        url = f'https://api.openweathermap.org/data/2.5/weather?q=Uira%C3%BAna,BR&units=metric&appid={api_key}'
        extract_data(url)

    @task
    def transform():
        os.makedirs('/opt/airflow/data', exist_ok=True)
        df = data_transformation_pipeline()
        df.to_parquet('/opt/airflow/data/temp_data.parquet', index=False)

    @task
    def load():
        import pandas as pd
        df = pd.read_parquet('/opt/airflow/data/temp_data.parquet')
        load_weather_data('uirauna_weather', df)

    extract() >> transform() >> load()


weather_pipeline()
