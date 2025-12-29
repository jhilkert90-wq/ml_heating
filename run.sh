#!/usr/bin/env bash

set -e

echo "[INFO] Starting ML Heating Control Add-on..."

# Initialize configuration
python3 /app/config_adapter.py

# Ensure directories
mkdir -p /data/{models,backups,logs,config}

# Start supervisor (runs ML Heating + Dashboard)
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
