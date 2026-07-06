# Weather, Air Quality and Marine Metrics Scraper
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd 
from datetime import datetime, timezone 
import time 

# Support function for cleaning and rounding values
def clean_val(val, decimals=2):
    if pd.isna(val): return None
    return round(float(val), decimals)

def extract_marine_data():
    
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    # Increased backoff factor for slower retry attempts if API gets stuck
    retry_session = retry(cache_session, retries=5, backoff_factor=0.5) 
    openmeteo = openmeteo_requests.Client(session=retry_session)

    marine_locations = {
        "Piraeus": {"lat": 37.94, "lon": 23.64},
        "Gibraltar": {"lat": 36.14, "lon": -5.35},
        "Rotterdam": {"lat": 51.99, "lon": 3.98},
        "Malacca": {"lat": 1.26, "lon": 103.82},
        "Cape_Horn": {"lat": -55.98, "lon": -67.27}
    }

    final_marine_data = []

    print("Webscraping started (Fetching 30-day History)...")

    for port_name, coords in marine_locations.items():
        lat = coords["lat"]
        lon = coords["lon"]
        
        try:
            # 1. WEATHER 
            url_weather = "https://api.open-meteo.com/v1/forecast"
            params_weather = {
                "latitude": lat, "longitude": lon, 
                "hourly": ["temperature_2m", "weather_code"],
                "past_days": 30, "forecast_days": 0
            }
            res_weather = openmeteo.weather_api(url_weather, params=params_weather)[0]
            hourly_weather = res_weather.Hourly()
            
            temp_array = hourly_weather.Variables(0).ValuesAsNumpy()
            wmo_array = hourly_weather.Variables(1).ValuesAsNumpy()

            # 2. AIR QUALITY 
            url_aq = "https://air-quality-api.open-meteo.com/v1/air-quality"
            params_aq = {
                "latitude": lat, "longitude": lon, 
                "hourly": ["european_aqi", "sulphur_dioxide", "nitrogen_dioxide", "dust", "pm2_5"],
                "past_days": 30, "forecast_days": 0
            }
            res_aq = openmeteo.weather_api(url_aq, params=params_aq)[0]
            hourly_aq = res_aq.Hourly()
            
            aqi_array = hourly_aq.Variables(0).ValuesAsNumpy()
            so2_array = hourly_aq.Variables(1).ValuesAsNumpy()
            no2_array = hourly_aq.Variables(2).ValuesAsNumpy()
            dust_array = hourly_aq.Variables(3).ValuesAsNumpy()
            pm25_array = hourly_aq.Variables(4).ValuesAsNumpy()

            # 3. MARINE DATA
            url_marine = "https://marine-api.open-meteo.com/v1/marine"
            params_marine = {
                "latitude": lat, "longitude": lon, 
                "hourly": ["wave_height", "wave_direction", "sea_surface_temperature", "ocean_current_velocity"],
                "past_days": 30, "forecast_days": 0
            }
            res_marine = openmeteo.weather_api(url_marine, params=params_marine)[0]
            hourly_marine = res_marine.Hourly()
            
            wave_height_array = hourly_marine.Variables(0).ValuesAsNumpy()
            wave_dir_array = hourly_marine.Variables(1).ValuesAsNumpy()
            sst_array = hourly_marine.Variables(2).ValuesAsNumpy()
            current_vel_array = hourly_marine.Variables(3).ValuesAsNumpy()

            # 4. TIME ARRAY & ZIP
            times = pd.date_range(
                start=pd.to_datetime(hourly_weather.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly_weather.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly_weather.Interval()),
                inclusive="left"
            )

            created_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

            for i in range(len(times)):
                port_record = {
                    "port_name": port_name,
                    "created_at": created_at,
                    "weather_time": times[i].strftime('%Y-%m-%d %H:%M:%S'),
                    "latitude": lat,
                    "longitude": lon,
                    "temperature_c": clean_val(temp_array[i], 1),
                    "wmo_code": int(wmo_array[i]) if not pd.isna(wmo_array[i]) else None,
                    "aqi_european": clean_val(aqi_array[i], 1),
                    "so2": clean_val(so2_array[i], 2),
                    "no2": clean_val(no2_array[i], 2),
                    "dust": clean_val(dust_array[i], 2),
                    "pm2_5": clean_val(pm25_array[i], 2),
                    "wave_height_m": clean_val(wave_height_array[i], 2),
                    "wave_direction_deg": clean_val(wave_dir_array[i], 1),
                    "sea_temperature_c": clean_val(sst_array[i], 1),
                    "ocean_current_velocity_kmh": clean_val(current_vel_array[i], 2)
                }
                final_marine_data.append(port_record)
                
            print(f"✅ Success at {port_name} (Loaded {len(times)} historical records)")

            # ΣΗΜΑΝΤΙΚΟ: Throttling / Rate Limiting
            # Περιμένουμε 15 δευτερόλεπτα πριν ζητήσουμε τα δεδομένα για το επόμενο λιμάνι
            # Αυτό δίνει χρόνο στον server του Open-Meteo να "ανασάνει" και αποτρέπει το 503 error.
            print(f"⏳ Sleeping for 15 seconds to respect API limits...")
            time.sleep(15)

        except Exception as e:
            print(f"❌ Error at {port_name}: {e}")

    return final_marine_data

if __name__ == "__main__":
    data = extract_marine_data()
    
    df = pd.DataFrame(data)
    print("\nFinal Dataset Info:")
    print(df.info())
    print(df.head())