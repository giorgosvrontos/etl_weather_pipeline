CREATE TABLE IF NOT EXISTS marine_weather_readings (
    id SERIAL PRIMARY KEY,              
    port_name VARCHAR(100) NOT NULL,    
    weather_time TIMESTAMP NOT NULL,    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    latitude NUMERIC,
    longitude NUMERIC,
    temperature_c NUMERIC,
    wmo_code INTEGER,
    weather_description VARCHAR(100),   
    aqi_european NUMERIC,
    so2 NUMERIC,
    no2 NUMERIC,
    dust NUMERIC,
    pm2_5 NUMERIC,
    wave_height_m NUMERIC,
    wave_direction_deg NUMERIC,
    sea_temperature_c NUMERIC,
    ocean_current_velocity_kmh NUMERIC,
    CONSTRAINT unique_port_time UNIQUE (port_name, weather_time)
);

--Creating indexes for performance optimization

CREATE INDEX IF NOT EXISTS idx_port_name ON marine_weather_readings(port_name);


CREATE INDEX IF NOT EXISTS idx_weather_time ON marine_weather_readings(weather_time);