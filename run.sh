#!/usr/bin/env bash

# ==============================================================================
# ML Heating Control Add-on Entry Point Script (with auto-restart)
# ==============================================================================

set -e

echo "[INFO] Starting ML Heating Control Add-on..."

# Initialize configuration
echo "[INFO] Initializing configuration..."
python3 /app/config_adapter.py

# Ensure data directories exist
mkdir -p /data/{models,backups,logs,config}

# Function to run ML Heating in a loop
run_ml_heating() {
    while true; do
        echo "[INFO] Starting ML Heating service..."
        python3 -m src.main >> /data/logs/ml_heating.log 2>&1
        EXIT_CODE=$?
        echo "[WARN] ML Heating exited with code $EXIT_CODE. Restarting in 5s..."
        sleep 5
    done
}

# Function to run Dashboard in a loop
run_dashboard() {
    while true; do
        echo "[INFO] Starting Dashboard service..."
        streamlit run /app/dashboard/app.py \
            --server.port=3001 \
            --server.address=0.0.0.0 \
            --server.headless=true \
            --server.enableCORS=false \
            --server.enableXsrfProtection=false \
            >> /data/logs/dashboard.log 2>&1
        EXIT_CODE=$?
        echo "[WARN] Dashboard exited with code $EXIT_CODE. Restarting in 5s..."
        sleep 5
    done
}

# Start both services in background
run_ml_heating &
run_dashboard &

# Wait for both background processes
wait
