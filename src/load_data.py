from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_engine():
    from dotenv import load_dotenv
    load_dotenv('/opt/airflow/config/.env')

    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME')
    host = os.getenv('DB_HOST', 'postgres')

    logging.info(f"→ Conectando em {host}:5432/{database}")
    return create_engine(
        f"postgresql+psycopg2://{user}:{quote_plus(password)}@{host}:5432/{database}"
    )


def load_weather_data(table_name: str, df):
    engine = get_engine()
    df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
    logging.info(f"Dados carregados com sucesso!")
    df_check = pd.read_sql(f'SELECT * FROM {table_name}', con=engine)
    logging.info(f"Total de registros na tabela: {len(df_check)}")
