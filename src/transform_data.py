import pandas as pd
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 

path_name = Path(__file__).parent.parent / 'data' / 'weather_data.json'
columns_names_to_drop = ['weather', 'weather_icon']
columns_names_to_rename = {
        "base": "base",
        "visibility": "visibility",
        "dt": "datetime",
        "timezone": "timezone",
        "id": "city_id", 
        "name": "city_name",
        "cod": "code",
        "coord.lon": "longitude",
        "coord.lat": "latitude",
        "main.temp": "temperature",
        "main.feels_like": "feels_like",
        "main.temp_min": "temp_min",
        "main.temp_max": "temp_max",
        "main.pressure": "pressure",
        "main.humidity": "humidity",
        "main.sea_level": "sea_level",
        "main.grnd_level": "grnd_level",
        "wind.speed": "wind_speed",
        "wind.deg": "wind_deg",
        "wind.gust": "wind_gust",
        "clouds.all": "clouds", 
        "sys.type": "sys_type",                 
        "sys.id": "sys_id",                
        "sys.country": "country",                
        "sys.sunrise": "sunrise",                
        "sys.sunset": "sunset",
        # weather_id, weather_main, weather_description 
    }
columns_to_normalize_datetime = ['datetime', 'sunrise', 'sunset']

def create_dataframe(path_name:str) -> pd.DataFrame:
    logging.info(f"Carregando dados do arquivo: {path_name}")
    path = path_name

    if not path.exists():
        raise FileNotFoundError(f"O arquivo {path_name} não foi encontrado.")
    
    with open(path_name) as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    return df


def normalize_weather_columns(df: pd.DataFrame) -> pd.DataFrame:

    df_weather = pd.json_normalize(df['weather'].apply(lambda x: x[0]))

    df_weather = df_weather.rename(columns={
        'id': 'weather_id',
        'main': 'weather_main',
        'description': 'weather_description',
        'icon': 'weather_icon'
    })

    df = pd.concat([df, df_weather], axis=1)
    logging.info(f"\n Colunas 'weather' normalizadas -{len(df_weather.columns)} e adicionadas ao DataFrame.")
    return df

def drop_columns(df: pd.DataFrame, columns_names:list[str]) -> pd.DataFrame:
    df = df.drop(columns=columns_names)
    logging.info(f"\n Colunas {columns_names} removidas do DataFrame.")
    return df

def rename_columns(df: pd.DataFrame, columns_names:dict[str, str]) -> pd.DataFrame:
    df = df.rename(columns=columns_names)
    logging.info(f"\n Colunas renomeadas: {columns_names}")
    return df

def normalize_datetime_columns(df: pd.DataFrame, columns_names:list[str]) -> pd.DataFrame:
    for name in columns_names:
        if name in df.columns:
            df[name] = pd.to_datetime(df[name], unit='s', utc=True).dt.tz_convert('America/Fortaleza')
    logging.info(f"\n Colunas {columns_names} normalizadas para formato datetime.")
    return df

def data_transformation_pipeline():
    print("Iniciando pipeline de transformação de dados...")
    df = create_dataframe(path_name)
    df = normalize_weather_columns(df)
    df = drop_columns(df, columns_names_to_drop)
    df = rename_columns(df, columns_names_to_rename)
    df = normalize_datetime_columns(df, columns_to_normalize_datetime)
    logging.info(f"\n Pipeline de transformação de dados concluída com sucesso.")  
    return df