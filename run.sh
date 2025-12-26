#!/bin/bash
# =======================================================================
# ML Heating Control Add-on Entry Point Script
# =======================================================================

set -e

echo "[INFO] Starting ML Heating Control Add-on..."

# ----------------------------------------------------------------------
# Detect Home Assistant environment
# ----------------------------------------------------------------------
if [[ -f "/etc/services.d" ]] || [[ -n "${SUPERVISOR_TOKEN}" ]]; then
    echo "[INFO] Running in Home Assistant Add-on environment"

    # Use bashio if available for additional config handling
    if command -v bashio &> /dev/null; then
        echo "[INFO] bashio detected, initializing configuration..."
        python3 /app/config_adapter.py
    else
        echo "[WARNING] bashio not available, continuing with environment variables"
    fi

    # Ensure Supervisor token is available
    if [[ -z "${SUPERVISOR_TOKEN}" ]]; then
        echo "[ERROR] Home Assistant Supervisor token not available!"
        exit 1
    fi
else
    echo "[INFO] Running in standalone/development mode"
    export SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN:-standalone_mode}"
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
