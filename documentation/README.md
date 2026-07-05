#  🌦️ ETL Weather Pipeline (Open-Meteo to PostgreSQL & Metabase)

A fully automated, modular, and **idempotent** Data Pipeline (ETL) developed in Python. This pipeline extracts meteorological, air quality, and marine data for specific ports from the **Open-Meteo API**, transforms the data, and loads it into a PostgreSQL database. Finally, the data is visualized through **Metabase**.

## 🚀 Features

* **Extract:** Pulls historical data for the **last 30 days** from 3 different Open-Meteo endpoints (Weather, Air Quality, Marine Weather).
* **Transform:** Consolidates the data and enriches the dataset. Specifically, it translates the `wmo_code` by adding a new `weather_description` column (e.g., converting `71` to `Snow fall` or `Rain`).
* **Load:** Stores the data in PostgreSQL. The process is strictly **idempotent**, ensuring no duplicate records are created if the pipeline is rerun.
* **Automation:** Utilizes a **Cronjob** to automatically execute the ETL process once a day.
* **Containerization:** The entire environment is fully dockerized, running across 3 Docker containers (Postgres, Python ETL App, Metabase).
* **Visualization:** Integrated Metabase container for instant Dashboard creation and SQL querying.

## 🛠️ Tech Stack

* **Programming Language:** Python 3
* **Database:** PostgreSQL
* **Business Intelligence (BI):** Metabase
* **Infrastructure / DevOps:** Docker, Docker Compose, Cron
* **API:** Open-Meteo (Free API)

## 📂 Project Structure

```text
ETL_WEATHER_PIPELINE/
├── data/
│   └── logs/                 # Log files (e.g., etl_run.log)
├── docker/
│   ├── .env                  # Environment variables (DB credentials, etc.)
│   ├── cronjob               # Daily cron job configuration
│   ├── docker-compose.yml    # Definition of the 3 services (db, app, metabase)
│   └── Dockerfile            # Instructions to build the Python container
├── documentation/            # Additional project documentation
├── sql_scripts/
│   └── init.sql              # Initial script for creating tables in Postgres
├── src/
│   ├── __pycache__/
│   ├── .cache.sqlite         # Cache file for API requests (if applicable)
│   ├── extract.py            # Logic for fetching data from the 3 APIs
│   ├── transform.py          # Data cleaning, merging, and feature engineering
│   ├── load.py               # Logic for connecting and inserting into PostgreSQL
│   └── main.py               # The main script that orchestrates the ETL process
├── .gitignore                # Files ignored by git
└── requirements.txt          # Python dependencies (e.g., pandas, sqlalchemy, requests)

## 📊 Data Schema

The final dataset stored in PostgreSQL includes the following fields:

| Column Name | Description |
| :--- | :--- |
| `port_name` | The name of the port / location |
| `created_at` | Timestamp indicating when the ETL was executed |
| `weather_time` | Timestamp of the actual measurement (hourly/daily) |
| `latitude` | Geographical latitude |
| `longitude` | Geographical longitude |
| `temperature_c` | Temperature in Celsius |
| `wmo_code` | Weather condition code based on the World Meteorological Organization |
| `weather_description`| **(Transform)** Explanatory text of the `wmo_code` (e.g., Rain, Clear) |
| `aqi_european` | European Air Quality Index (AQI) |
| `so2` | Sulfur Dioxide concentration |
| `no2` | Nitrogen Dioxide concentration |
| `dust` | Dust concentration |
| `pm2_5` | Particulate Matter 2.5 concentration |
| `wave_height_m` | Wave height in meters |
| `wave_direction_deg` | Wave direction in degrees |
| `sea_temperature_c` | Sea temperature in Celsius |
| `ocean_current_velocity_kmh` | Ocean current velocity in km/h |

## ⚙️ Setup Instructions

**Prerequisites:** You must have Docker and Docker Compose installed on your system.

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd ETL_WEATHER_PIPELINE
    ```

2.  **Configure Environment Variables:**
    Navigate to the `docker/` folder and ensure the `.env` file contains the correct database configurations:
    ```env
    POSTGRES_USER=your_user
    POSTGRES_PASSWORD=your_password
    POSTGRES_DB=weather_db
    ```

3.  **Start the Services:**
    From the root directory of the project (or inside the docker folder, depending on where your compose file is located), run:
    ```bash
    docker-compose -f docker/docker-compose.yml up -d --build
    ```
    This command will spin up:
    * **PostgreSQL** on port `5432` (automatically executing `init.sql`).
    * The **Python ETL Container**, which will initialize the cronjob.
    * **Metabase** on port `3000`.

## 📈 Metabase Dashboards

Once the containers are up and the initial ETL pipeline has run:

1.  Open your browser and navigate to: `http://localhost:3000`
2.  Complete the initial Metabase setup.
3.  Connect your database by selecting PostgreSQL and entering the credentials from your `.env` file (for the host, use the DB service name, e.g., `postgres`).
4.  You can now execute SQL Queries and create interactive Dashboards with your port data!

## 🔄 Cronjob & Logging

The ETL pipeline is configured to run automatically every day.

* **Idempotency:** The logic inside `load.py` (typically using `INSERT ... ON CONFLICT DO UPDATE` or checking existing records) ensures that the 30-day data is not duplicated upon rerun.
* **Logs:** Every execution of the pipeline is recorded in `data/logs/etl_run.log`, allowing for easy monitoring and debugging.


