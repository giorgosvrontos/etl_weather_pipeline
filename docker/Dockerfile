FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Copying the cron job file to the cron.d directory
COPY docker/cronjob /etc/cron.d/etl-cron

# Giving permissions to the cron job file
RUN chmod 0644 /etc/cron.d/etl-cron

RUN crontab /etc/cron.d/etl-cron

# Creating the log file for cron job output
RUN mkdir -p /app/data/logs && touch /app/data/logs/etl_run.log


CMD ["cron", "-f"]