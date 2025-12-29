#!/usr/bin/with-contenv bashio

# ==============================================================================
# ML Heating Control Add-on Entry Point Script
# ==============================================================================

set -e

# Configure logging
bashio::log.info "Starting ML Heating Control Add-on..."

# Initialize configuration
bashio::log.info "Initializing configuration..."
python3 /app/config_adapter.py

# Setup data directories
mkdir -p /data/{models,backups,logs,config}
chown -R root:root /data

# Import existing model if specified
if bashio::config.true 'import_existing_model' && bashio::config.has_value 'existing_model_path'; then
    MODEL_PATH=$(bashio::config 'existing_model_path')
    if [[ -f "${MODEL_PATH}" ]]; then
        bashio::log.info "Importing existing model from ${MODEL_PATH}..."
        cp "${MODEL_PATH}" /data/models/ml_model.pkl
        bashio::log.info "Model imported successfully"
    else
        bashio::log.warning "Specified model path does not exist: ${MODEL_PATH}"
    fi
fi

# Create log file if it doesn't exist
touch /data/logs/ml_heating.log

# =========================
# Optional: Start single service
# =========================
# Usage: run.sh [ml_heating|dashboard]
SERVICE="${1:-supervisor}"


if [[ "$SERVICE" == "ml_heating" ]]; then
    bashio::log.info "Starting ML Heating service..."
    exec python3 -m src.main

elif [[ "$SERVICE" == "dashboard" ]]; then
    bashio::log.info "Starting Dashboard..."
    exec python3 -m streamlit run /app/dashboard/app.py \
        --server.port=3001 \
        --server.address=0.0.0.0 \
        --server.headless=true \
        --server.enableCORS=false \
        --server.enableXsrfProtection=false

else
    # Default: start supervisord to manage all services
    bashio::log.info "Starting services with supervisor..."
    exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
fi
