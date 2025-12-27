#!/usr/bin/with-contenv bashio
set -e

echo "[INFO] Starting ML Heating Control Add-on..."

# Set Supervisor token if running in HA addon
if [ -n "$SUPERVISOR_TOKEN" ]; then
    export HASS_URL="http://supervisor/core"
    echo "[INFO] Using Supervisor API at $HASS_URL"
else
    echo "[ERROR] Supervisor token not available! Add-on must run in HA environment."
    exit 1
fi

# Ensure data dirs exist
mkdir -p /data/{models,backups,logs,config}
touch /data/logs/ml_heating.log

# Start ML backend
echo "[INFO] Starting ML backend..."
python3 -m src.main &

# Start Streamlit dashboard
echo "[INFO] Starting Dashboard on port 3001..."
exec streamlit run /app/dashboard/app.py \
    --server.port=3001 \
    --server.address=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --server.headless=true
