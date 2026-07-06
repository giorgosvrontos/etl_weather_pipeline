--percentage of null values
SELECT 
    port_name,
    COUNT(*) AS total_records,
    MIN(weather_time) AS first_record_date,
    MAX(weather_time) AS last_record_date,
    ROUND((COUNT(*) FILTER (WHERE temperature_c IS NULL) * 100.0 / COUNT(*)), 2) AS missing_temp_percentage,
    ROUND((COUNT(*) FILTER (WHERE wave_height_m IS NULL) * 100.0 / COUNT(*)), 2) AS missing_wave_percentage
FROM 
    marine_weather_readings
GROUP BY 
    port_name
ORDER BY 
    port_name;


--pin map 
WITH LatestConditions AS (
    SELECT 
        port_name, 
        latitude, 
        longitude, 
        temperature_c, 
        wave_height_m, 
        weather_description,
        ROW_NUMBER() OVER(PARTITION BY port_name ORDER BY weather_time DESC) as rn
    FROM 
        marine_weather_readings
)
SELECT 
    port_name, 
    latitude, 
    longitude, 
    temperature_c, 
    wave_height_m,
    weather_description
FROM 
    LatestConditions 
WHERE 
    rn = 1;

--daily sum up 
SELECT 
    port_name,
    DATE(weather_time) AS reading_date,
    ROUND(AVG(temperature_c), 1) AS avg_daily_temp,
    MAX(temperature_c) AS max_daily_temp,
    ROUND(AVG(wave_height_m), 2) AS avg_wave_height,
    MAX(wave_height_m) AS max_wave_height,
    ROUND(AVG(aqi_european), 1) AS avg_air_quality_index
FROM 
    marine_weather_readings
GROUP BY 
    port_name, 
    DATE(weather_time)
ORDER BY 
    reading_date DESC, 
    port_name;