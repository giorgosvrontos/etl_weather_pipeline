# Weather, Air Quality and Marine Metrics Scraper
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd 
from datetime import datetime, timezone 

def extract_marine_data():
    
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    marine_locations = {
        "Piraeus": {"lat": 37.94, "lon": 23.64},
        "Gibraltar": {"lat": 36.14, "lon": -5.35},
        "Rotterdam": {"lat": 51.99, "lon": 3.98},
        "Malacca": {"lat": 1.26, "lon": 103.82},
        "Cape_Horn": {"lat": -55.98, "lon": -67.27}
    }

    final_marine_data = []

    print("Webscraping started...")

    for port_name, coords in marine_locations.items():
        lat = coords["lat"]
        lon = coords["lon"]
        
        try:
            # WEATHER
            url_weather = "https://api.open-meteo.com/v1/forecast"
            params_weather = {"latitude": lat, "longitude": lon, "current": ["temperature_2m", "weather_code"]}
            res_weather = openmeteo.weather_api(url_weather, params=params_weather)[0].Current()
            
            temp = res_weather.Variables(0).Value()
            wmo = res_weather.Variables(1).Value()

            # AIR QUALITY 
            url_aq = "https://air-quality-api.open-meteo.com/v1/air-quality"
            params_aq = {"latitude": lat, "longitude": lon, "current": ["european_aqi", "sulphur_dioxide", "nitrogen_dioxide", "dust", "pm2_5"]}
            res_aq = openmeteo.weather_api(url_aq, params=params_aq)[0].Current()
            
            aqi = res_aq.Variables(0).Value()
            so2 = res_aq.Variables(1).Value()
            no2 = res_aq.Variables(2).Value()
            dust = res_aq.Variables(3).Value()
            pm25 = res_aq.Variables(4).Value()

            # MARINE DATA
            url_marine = "https://marine-api.open-meteo.com/v1/marine"
            params_marine = {"latitude": lat, "longitude": lon, "current": ["wave_height", "wave_direction", "sea_surface_temperature", "ocean_current_velocity"]}
            res_marine = openmeteo.weather_api(url_marine, params=params_marine)[0].Current()
            
            wave_height = res_marine.Variables(0).Value()
            wave_dir = res_marine.Variables(1).Value()
            sst = res_marine.Variables(2).Value()
            current_vel = res_marine.Variables(3).Value()

            
            created_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            
            api_unix_time = res_weather.Time() 

            weather_time = datetime.fromtimestamp(api_unix_time, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

            port_record = {
                "port_name": port_name,
                "created_at": created_at,
                "weather_time": weather_time,
                "latitude": lat,
                "longitude": lon,
                "temperature_c": round(float(temp), 1),
                "wmo_code": int(wmo),
                "aqi_european": round(float(aqi), 1),
                "so2": round(float(so2), 2),
                "no2": round(float(no2), 2),
                "dust": round(float(dust), 2),
                "pm2_5": round(float(pm25), 2),
                "wave_height_m": round(float(wave_height), 2),
                "wave_direction_deg": round(float(wave_dir), 1),
                "sea_temperature_c": round(float(sst), 1),
                "ocean_current_velocity_kmh": round(float(current_vel), 2)
            }

            final_marine_data.append(port_record)
            print(f"✅ Success at {port_name}")

        except Exception as e:
            print(f"❌ Error at {port_name}: {e}")

    return final_marine_data

if __name__ == "__main__":
    data = extract_marine_data()
    
    df = pd.DataFrame(data)
    print("Final Dataset")
    print(df.to_string())