#!/bin/bash
# ==============================================================================
# ML Heating Control Add-on Entry Point Script (with Dashboard)
# ==============================================================================

set -e

echo "[INFO] Starting ML Heating Control Add-on..."

# ------------------------------------------------------------------------------
# Detect Home Assistant Add-on environment
# ------------------------------------------------------------------------------
if [[ -n "${SUPERVISOR_TOKEN}" ]]; then
    echo "[INFO] Running in Home Assistant Add-on environment"

    if command -v bashio &> /dev/null; then
        echo "[INFO] Initializing configuration via bashio"
        python3 /app/config_adapter.py
    else
        echo "[WARN] bashio not available, continuing without it"
    fi
else
    echo "[INFO] Running in standalone/development mode"
    export SUPERVISOR_TOKEN="standalone"
fi

# ------------------------------------------------------------------------------
# Prepare data directories
# ------------------------------------------------------------------------------
mkdir -p /data/{models,backups,logs,config}
touch /data/logs/ml_heating.log

# ------------------------------------------------------------------------------
# Start ML Heating main loop (background)
# ------------------------------------------------------------------------------
echo "[INFO] Starting ML Heating core loop"
python3 -m src.main &

# ------------------------------------------------------------------------------
# Start Streamlit Dashboard (Ingress on port 3001)
# ------------------------------------------------------------------------------
echo "[INFO] Starting Streamlit dashboard on port 3001"

export STREAMLIT_SERVER_PORT=3001
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_BASE_URL_PATH="${HASSIO_INGRESS_PATH:-/}"

exec streamlit run /app/dashboard/app.py
