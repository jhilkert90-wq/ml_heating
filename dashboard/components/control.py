"""
ML Heating Dashboard - Control Component
System control interface for ML heating management
"""

import streamlit as st
import json
import os
import subprocess
from datetime import datetime
import sys
import signal

# Add app directory to Python path
sys.path.append('/app')

ML_PID_FILE = '/data/config/ml_pid.txt'
RECALIBRATE_FLAG = '/data/config/recalibrate_flag'


def get_ml_system_status():
    """Check if ML system process is running"""
    if os.path.exists(ML_PID_FILE):
        try:
            with open(ML_PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # check if process exists
            return True
        except Exception:
            return False
    return False


def start_ml_system():
    """Start ML system in background"""
    if get_ml_system_status():
        return False, "ML system already running"
    
    # Start the ML process in background
    process = subprocess.Popen(
        ['python3', '/app/src/main.py'],
        stdout=open('/data/logs/ml_heating.log', 'a'),
        stderr=subprocess.STDOUT
    )
    # Save PID
    with open(ML_PID_FILE, 'w') as f:
        f.write(str(process.pid))
    return True, f"ML system started with PID {process.pid}"


def stop_ml_system():
    """Stop ML system using PID"""
    if not os.path.exists(ML_PID_FILE):
        return False, "ML system not running"
    
    try:
        with open(ML_PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        os.remove(ML_PID_FILE)
        return True, "ML system stopped"
    except Exception as e:
        return False, f"Failed to stop ML system: {e}"


def restart_ml_system():
    """Restart ML system"""
    stop_ml_system()
    return start_ml_system()


def trigger_model_recalibration():
    """Trigger model recalibration"""
    try:
        # Write recalibration flag
        with open(RECALIBRATE_FLAG, 'w') as f:
            f.write(datetime.now().isoformat())
        # Restart ML system
        success, output = restart_ml_system()
        return success, "Recalibration triggered. " + output
    except Exception as e:
        return False, str(e)


def load_current_config():
    """Load add-on configuration"""
    try:
        with open('/data/options.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return {}


def save_config_changes(config):
    """Save configuration changes"""
    try:
        with open('/data/config/pending_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        return True, "Configuration saved. Restart add-on to apply changes."
    except Exception as e:
        return False, str(e)


# ------------------------------
# Streamlit rendering functions
# ------------------------------

def render_system_controls():
    """Render system control buttons"""
    st.subheader("🎛️ System Controls")
    
    is_running = get_ml_system_status()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Restart System"):
            with st.spinner("Restarting ML system..."):
                success, output = restart_ml_system()
                if success:
                    st.success(output)
                else:
                    st.error(output)
    
    with col2:
        if is_running:
            if st.button("⏹️ Stop System"):
                with st.spinner("Stopping ML system..."):
                    success, output = stop_ml_system()
                    if success:
                        st.success(output)
                    else:
                        st.error(output)
        else:
            if st.button("▶️ Start System"):
                with st.spinner("Starting ML system..."):
                    success, output = start_ml_system()
                    if success:
                        st.success(output)
                    else:
                        st.error(output)
    
    with col3:
        if st.button("🔧 Recalibrate Model"):
            with st.spinner("Triggering model recalibration..."):
                success, output = trigger_model_recalibration()
                if success:
                    st.success("Model recalibration started!")
                    st.info("This will reset learning progress and retrain from historical data.")
                else:
                    st.error(f"Recalibration failed: {output}")


# ------------------------------
# Optional: other controls
# ------------------------------

def render_control():
    """Main control page"""
    st.header("🎛️ System Control")
    if get_ml_system_status():
        st.success("🟢 ML System Status: Running")
    else:
        st.error("🔴 ML System Status: Stopped")
    
    st.divider()
    render_system_controls()
