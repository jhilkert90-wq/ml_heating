#!/bin/bash
# =======================================================================
# ML Heating Control Add-on Entry Point Script
# =======================================================================

set -e

echo "[INFO] Starting ML Heating Control Add-on..."

# ----------------------------------------------------------------------
# Home Assistant Add-on environment
# ----------------------------------------------------------------------
if [[ -z "${SUPERVISOR_TOKEN}" ]]; then
    echo "[ERROR] Home Assistant Supervisor token not available!"
    exit 1
fi

echo "[INFO] Supervisor token detected, running in HA Add-on environment"

# ----------------------------------------------------------------------
# Initialize configuration if bashio is available
# ----------------------------------------------------------------------
if command -v bashio &> /dev/null; then
    echo "[INFO] bashio detected, initializing configuration..."
    python3 /app/config_adapter.py
fi

# ----------------------------------------------------------------------
# Create data directories and logs
# ----------------------------------------------------------------------
mkdir -p /data/{models,backups,logs,config}
touch /data/logs/ml_heating.log

# ----------------------------------------------------------------------
# Start ML backend (non-blocking)
# ----------------------------------------------------------------------
echo "[INFO] Starting ML backend..."
python3 -m src.main &

# ----------------------------------------------------------------------
# Start Streamlit Dashboard
# ----------------------------------------------------------------------
echo "[INFO] Starting Dashboard on port 3001..."
exec streamlit run /app/dashboard/app.py \
    --server.port=3001 \
    --server.address=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --server.headless=true
