#!/usr/bin/with-contenv bashio
set -e

bashio::log.info "Starting ML Heating Add-on..."

# Init config
python3 /app/config_adapter.py

# Ensure data dirs
mkdir -p /data/{models,backups,logs,config}

bashio::log.info "Starting ML Heating service..."
python3 -m src.main &

bashio::log.info "Starting Dashboard service..."
python3 -m streamlit run /app/dashboard/app.py \
    --server.port=3001 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false &

wait
