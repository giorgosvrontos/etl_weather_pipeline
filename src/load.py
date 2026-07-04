import os
import time
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv  

ENV_PATH = "/app/docker/.env"

load_dotenv(dotenv_path=ENV_PATH)

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "postgres_db"),
    "dbname":   os.getenv("DB_NAME", "weather_db"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port":     os.getenv("DB_PORT", "5432"),
}

def load_data_to_postgres(transformed_data):
   
    if not transformed_data:
        print("⚠️ No data to load.")
        return

    print(f"Loading {len(transformed_data)} records to the database...")

    # Το SQL Query με το ON CONFLICT DO NOTHING (UPSERT)
    insert_query = """
        INSERT INTO marine_weather_readings (
            port_name, weather_time, created_at, latitude, longitude,
            temperature_c, wmo_code, weather_description,
            aqi_european, so2, no2, dust, pm2_5,
            wave_height_m, wave_direction_deg, sea_temperature_c, ocean_current_velocity_kmh
        ) VALUES (
            %(port_name)s, %(weather_time)s, %(created_at)s, %(latitude)s, %(longitude)s,
            %(temperature_c)s, %(wmo_code)s, %(weather_description)s,
            %(aqi_european)s, %(so2)s, %(no2)s, %(dust)s, %(pm2_5)s,
            %(wave_height_m)s, %(wave_direction_deg)s, %(sea_temperature_c)s, %(ocean_current_velocity_kmh)s
        )
        ON CONFLICT (port_name, weather_time) DO NOTHING;
    """

    conn = None
    try:
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        
        execute_batch(cursor, insert_query, transformed_data)

        
        conn.commit()
        
        print("✅ The data was loaded successfully to the PostgreSQL!")

    except Exception as e:
        print(f"❌ Error occurred while loading data to the database: {e}")
        if conn:
            conn.rollback()

    finally:
        
        if conn:
            cursor.close()
            conn.close()