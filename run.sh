#!/bin/bash
set -e

echo "[INFO] Starting ML Heating Control Add-on..."

# ------------------------------------------------------------------------------
# Home Assistant Add-on Environment Detection
# ------------------------------------------------------------------------------
if command -v bashio &> /dev/null; then
    echo "[INFO] Home Assistant Add-on environment detected via bashio"
    
    # Set Supervisor token for HA API access
    export SUPERVISOR_TOKEN=$(bashio::auth.supervisor)
    
    # Initialize configuration
    echo "[INFO] Initializing configuration via config_adapter.py"
    python3 /app/config_adapter.py
else
    echo "[INFO] Standalone mode"
    export SUPERVISOR_TOKEN="standalone"
fi

# ------------------------------------------------------------------------------
# Data directories
# ------------------------------------------------------------------------------
mkdir -p /data/{models,backups,logs,config}
touch /data/logs/ml_heating.log

# ------------------------------------------------------------------------------
# Start ML backend (non-blocking)
# ------------------------------------------------------------------------------
echo "[INFO] Starting ML backend..."
python3 -m src.main &

# ------------------------------------------------------------------------------
# Start Streamlit Dashboard (Ingress Port!)
# ------------------------------------------------------------------------------
echo "[INFO] Starting Dashboard on port 3001..."
exec streamlit run /app/dashboard/app.py \
    --server.port=3001 \
    --server.address=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --server.headless=true
