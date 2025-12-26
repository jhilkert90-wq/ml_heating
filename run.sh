#!/usr/bin/with-contenv bash
# ==============================================================================
# ML Heating Control Add-on Entry Point Script
# - Starts ML engine
# - Starts Streamlit dashboard (Ingress compatible)
# ==============================================================================

set -e

echo "[INFO] Starting ML Heating Control Add-on..."

# ------------------------------------------------------------------------------
# Detect Home Assistant environment
# ------------------------------------------------------------------------------
IS_HA=false
if [[ -n "${SUPERVISOR_TOKEN}" ]] || [[ -d "/etc/services.d" ]]; then
    IS_HA=true
fi

# ------------------------------------------------------------------------------
# Initialize configuration
# ------------------------------------------------------------------------------
if $IS_HA; then
    echo "[INFO] Home Assistant Add-on environment detected"

    if command -v bashio &>/dev/null; then
        echo "[INFO] Initializing configuration via bashio"
        python3 /app/config_adapter.py
    else
        echo "[WARN] bashio not found, skipping HA config adapter"
    fi
else
    echo "[INFO] Standalone mode detected"
    export SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN:-standalone}"
fi

# ------------------------------------------------------------------------------
# Prepare directories
# ------------------------------------------------------------------------------
mkdir -p /data/{models,backups,logs,config}

touch /data/logs/ml_heating.log

# ------------------------------------------------------------------------------
# Environment defaults
# ------------------------------------------------------------------------------
export PYTHONUNBUFFERED=1
export STREAMLIT_SERVER_PORT=3001
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_THEME_BASE=light

# Home Assistant Ingress support
if [[ -n "${HASSIO_INGRESS_PATH}" ]]; then
    echo "[INFO] Home Assistant ingress detected at ${HASSIO_INGRESS_PATH}"
    export STREAMLIT_SERVER_BASE_URL_PATH="${HASSIO_INGRESS_PATH}"
fi

# ------------------------------------------------------------------------------
# Start ML engine (background)
# ------------------------------------------------------------------------------
echo "[INFO] Starting ML heating engine..."
python3 -m src.main >> /data/logs/ml_heating.log 2>&1 &

ML_PID=$!
echo "[INFO] ML engine started with PID ${ML_PID}"

# ------------------------------------------------------------------------------
# Start Dashboard (Streamlit)
# ------------------------------------------------------------------------------
echo "[INFO] Starting Dashboard on port 3001..."

exec streamlit run \
    /app/dashboard/app.py \
    --server.port=3001 \
    --server.address=0.0.0.0
