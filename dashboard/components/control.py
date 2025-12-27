"""
ML Heating Dashboard - Control Component
System control interface for ML heating management
Uses Supervisor API for add-on control
"""

import streamlit as st
import json
import os
import requests
from datetime import datetime
import sys

# Add app directory to Python path
sys.path.append('/app')

# Supervisor API configuration
SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
SUPERVISOR_API = "http://supervisor/core/api"
ADDON_SLUG = "ml_heating"  # Dein Add-on-Slug

HEADERS = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}

def call_supervisor_service(service: str):
    """Call HA Supervisor API for the ML Heating Add-on"""
    url = f"{SUPERVISOR_API}/addons/{ADDON_SLUG}/{service}"
    try:
        r = requests.post(url, headers=HEADERS, timeout=10)
        if r.status_code in (200, 204):
            return True, r.text or f"{service} executed successfully."
        else:
            return False, f"{service} failed: {r.status_code} {r.text}"
    except Exception as e:
        return False, str(e)

# ----------------------------
# System status and control
# ----------------------------
def get_ml_system_status():
    """Check if ML system is running using Supervisor API"""
    try:
        url = f"{SUPERVISOR_API}/addons/{ADDON_SLUG}/info"
        r = requests.get(url, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data.get("state") == "started"
        return False
    except Exception:
        return False

def restart_ml_system():
    return call_supervisor_service("restart")

def stop_ml_system():
    return call_supervisor_service("stop")

def start_ml_system():
    return call_supervisor_service("start")

def trigger_model_recalibration():
    """Trigger model recalibration by creating flag file and restarting add-on"""
    try:
        os.makedirs("/data/config", exist_ok=True)
        with open('/data/config/recalibrate_flag', 'w') as f:
            f.write(datetime.now().isoformat())
        success, output = restart_ml_system()
        return success, "Recalibration triggered. " + output
    except Exception as e:
        return False, str(e)

# ----------------------------
# Configuration handling
# ----------------------------
def load_current_config():
    """Load current add-on configuration"""
    try:
        with open('/data/options.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return {}

def save_config_changes(config):
    """Save configuration changes (requires add-on restart)"""
    try:
        os.makedirs("/data/config", exist_ok=True)
        with open('/data/config/pending_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        return True, "Configuration saved. Restart add-on to apply changes."
    except Exception as e:
        return False, str(e)

# ----------------------------
# UI Components
# ----------------------------
def render_system_controls():
    st.subheader("🎛️ System Controls")
    is_running = get_ml_system_status()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔄 Restart System", type="primary"):
            with st.spinner("Restarting ML system..."):
                success, output = restart_ml_system()
                if success:
                    st.success("System restarted successfully!")
                else:
                    st.error(f"Restart failed: {output}")

    with col2:
        if is_running:
            if st.button("⏹️ Stop System", type="secondary"):
                with st.spinner("Stopping ML system..."):
                    success, output = stop_ml_system()
                    if success:
                        st.success("System stopped successfully!")
                    else:
                        st.error(f"Stop failed: {output}")
        else:
            if st.button("▶️ Start System", type="primary"):
                with st.spinner("Starting ML system..."):
                    success, output = start_ml_system()
                    if success:
                        st.success("System started successfully!")
                    else:
                        st.error(f"Start failed: {output}")

    with col3:
        if st.button("🔧 Recalibrate Model"):
            with st.spinner("Triggering model recalibration..."):
                success, output = trigger_model_recalibration()
                if success:
                    st.success("Model recalibration started!")
                    st.info("This will reset learning progress and retrain from historical data.")
                else:
                    st.error(f"Recalibration failed: {output}")

    with col4:
        if st.button("📋 View Logs"):
            st.session_state['show_logs'] = True

def render_mode_controls():
    st.subheader("🔀 Operating Mode")
    current_mode = st.radio(
        "Select operating mode:",
        ["Active Mode", "Shadow Mode"],
        help="""
        - **Active Mode**: ML system controls heating directly
        - **Shadow Mode**: ML system observes but doesn't control heating
        """
    )
    if current_mode == "Shadow Mode":
        st.info("**Shadow Mode**: Safe testing without affecting heating")
    else:
        st.success("**Active Mode**: ML system optimizes heating directly")
    
    if st.button("Apply Mode Change"):
        st.warning("Mode changes require add-on configuration update and restart.")

def render_manual_controls():
    st.subheader("🌡️ Manual Override")
    st.warning("⚠️ Use manual overrides carefully!")

def render_log_viewer():
    if st.session_state.get('show_logs', False):
        st.subheader("📋 System Logs")
        st.text("Log viewer functionality here...")

def render_configuration_editor():
    st.subheader("⚙️ Live Configuration")
    config = load_current_config()
    if not config:
        st.error("Unable to load configuration")
        return
    st.info("Configuration changes require add-on restart to take effect.")

def render_control():
    st.header("🎛️ System Control")
    is_running = get_ml_system_status()
    if is_running:
        st.success("🟢 ML System Status: Running")
    else:
        st.error("🔴 ML System Status: Stopped")
    
    st.divider()
    render_system_controls()
    st.divider()
    render_mode_controls()
    st.divider()
    render_manual_controls()
    st.divider()
    render_configuration_editor()
    if st.session_state.get('show_logs', False):
        st.divider()
        render_log_viewer()
