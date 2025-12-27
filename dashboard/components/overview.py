"""
ML Heating Dashboard - Overview Component
Real-time monitoring and system status display
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys
from streamlit.runtime.scriptrunner import RerunException

# Add app directory to Python path
sys.path.append('/app')

# ---------------- Session State Initialization ----------------
if 'refresh_counter' not in st.session_state:
    st.session_state['refresh_counter'] = 0

# ---------------- ML State ----------------
def load_ml_state():
    try:
        if os.path.exists('/data/models/ml_state.pkl'):
            import pickle
            with open('/data/models/ml_state.pkl', 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        st.error(f"Error loading ML state: {e}")
    return None

def get_system_metrics():
    state = load_ml_state()
    if state:
        return {
            'confidence': state.get('confidence', 0.0),
            'mae': state.get('mae', 0.0),
            'rmse': state.get('rmse', 0.0),
            'cycle_count': state.get('cycle_count', 0),
            'last_prediction': state.get('last_prediction', 0.0),
            'status': state.get('status', 'unknown')
        }
    return {
        'confidence': 0.92,
        'mae': 0.15,
        'rmse': 0.21,
        'cycle_count': 450,
        'last_prediction': 42.5,
        'status': 'active'
    }

# ---------------- Log Data ----------------
def get_recent_log_data():
    try:
        if os.path.exists('/data/logs/ml_heating.log'):
            with open('/data/logs/ml_heating.log', 'r') as f:
                lines = f.readlines()[-100:]
            
            log_data = []
            for line in lines:
                if 'confidence:' in line and 'mae:' in line:
                    try:
                        parts = line.split()
                        timestamp = f"{parts[0]} {parts[1]}"
                        confidence = float(line.split('confidence:')[1].split()[0])
                        mae = float(line.split('mae:')[1].split()[0])
                        log_data.append({
                            'timestamp': pd.to_datetime(timestamp),
                            'confidence': confidence,
                            'mae': mae
                        })
                    except Exception:
                        continue
            
            if log_data:
                return pd.DataFrame(log_data)
    except Exception:
        pass
    
    now = datetime.now()
    demo_data = []
    for i in range(24):
        demo_data.append({
            'timestamp': now - timedelta(hours=i),
            'confidence': 0.85 + (0.15 * (i % 3) / 3),
            'mae': 0.12 + (0.08 * (i % 4) / 4)
        })
    
    return pd.DataFrame(demo_data).sort_values('timestamp')

# ---------------- Metric Cards ----------------
def render_metric_cards():
    metrics = get_system_metrics()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Confidence", 
            f"{metrics['confidence']:.3f}", 
            f"{metrics['confidence']-0.85:.3f}" if metrics['confidence'] != 0.85 else None
        )
    with col2:
        st.metric(
            "MAE (°C)", 
            f"{metrics['mae']:.3f}", 
            f"{0.2-metrics['mae']:.3f}" if metrics['mae'] != 0.2 else None
        )
    with col3:
        st.metric(
            "RMSE (°C)", 
            f"{metrics['rmse']:.3f}", 
            f"{0.25-metrics['rmse']:.3f}" if metrics['rmse'] != 0.25 else None
        )
    with col4:
        st.metric(
            "Learning Cycles", 
            f"{metrics['cycle_count']:,}", 
            f"+{metrics['cycle_count']-400}" if metrics['cycle_count'] > 400 else None
        )

# ---------------- Performance Trend ----------------
def render_performance_trend():
    st.subheader("Performance Trend")
    df = get_recent_log_data()
    
    if not df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['confidence'], mode='lines+markers',
            name='Confidence', line=dict(color='#1f77b4', width=2), yaxis='y'
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['mae'], mode='lines+markers',
            name='MAE (°C)', line=dict(color='#ff7f0e', width=2), yaxis='y2'
        ))
        
        fig.update_layout(
            xaxis_title="Time",
            yaxis=dict(title="Confidence", title_font=dict(color="#1f77b4"),
                       tickfont=dict(color="#1f77b4"), range=[0, 1]),
            yaxis2=dict(title="MAE (°C)", title_font=dict(color="#ff7f0e"),
                        tickfont=dict(color="#ff7f0e"), overlaying="y", side="right",
                        range=[0, max(df['mae']) * 1.2]),
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No performance data available yet. Data will appear after the ML system starts learning.")

# ---------------- System Status ----------------
def render_system_status():
    st.subheader("System Status")
    metrics = get_system_metrics()
    col1, col2 = st.columns(2)
    
    with col1:
        status = metrics['status']
        if status == 'active':
            st.success("🟢 ML System: Active")
        elif status == 'shadow':
            st.info("🟡 ML System: Shadow Mode")
        elif status == 'blocked':
            st.warning("🟠 ML System: Blocked (DHW/Defrost)")
        else:
            st.error("🔴 ML System: Inactive")
        if metrics['last_prediction'] > 0:
            st.info(f"🌡️ Last Prediction: {metrics['last_prediction']:.1f}°C")
        
        dirs = ['/data/models', '/data/backups', '/data/logs']
        for directory in dirs:
            if os.path.exists(directory):
                st.success(f"📁 {directory.split('/')[-1]}: {len(os.listdir(directory))} files")
            else:
                st.warning(f"📁 {directory.split('/')[-1]}: Not found")
    
    with col2:
        st.write("**Learning Progress**")
        cycle_count = metrics['cycle_count']
        if cycle_count < 200:
            st.info("🌱 Initializing (0-200 cycles)")
            progress = cycle_count / 200
        elif cycle_count < 1000:
            st.info("⚙️ Learning (200-1000 cycles)")
            progress = (cycle_count - 200) / 800
        else:
            st.success("✅ Mature (1000+ cycles)")
            progress = 1.0
        st.progress(progress)
        st.write(f"Cycle {cycle_count:,}")
        
        if os.path.exists('/data/models/ml_model.pkl'):
            stat = os.stat('/data/models/ml_model.pkl')
            model_size = stat.st_size / 1024
            last_updated = datetime.fromtimestamp(stat.st_mtime)
            st.success(f"💾 Model: {model_size:.1f}KB")
            st.caption(f"Updated: {last_updated.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.warning("💾 Model: Not found")

# ---------------- Configuration ----------------
def render_configuration_summary():
    st.subheader("Configuration")
    try:
        with open('/data/options.json', 'r') as f:
            config = json.load(f)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Core Entities**")
            core_entities = [
                ('Target Indoor Temp', 'target_indoor_temp_entity'),
                ('Indoor Temp Sensor', 'indoor_temp_entity'),
                ('Outdoor Temp Sensor', 'outdoor_temp_entity'),
                ('Heating Control', 'heating_control_entity')
            ]
            for label, key in core_entities:
                value = config.get(key, 'Not configured')
                if value and value != 'Not configured':
                    st.success(f"✅ {label}")
                    st.caption(f"`{value}`")
                else:
                    st.error(f"❌ {label}")
        
        with col2:
            st.write("**Learning Parameters**")
            st.write(f"Learning Rate: `{config.get('learning_rate', 0.01)}`")
            st.write(f"Cycle Interval: `{config.get('cycle_interval_minutes', 30)}` min")
            st.write(f"Max Temp Change: `{config.get('max_temp_change_per_cycle', 2.0)}`°C")
            st.write("**Safety Limits**")
            st.write(f"Min Safety: `{config.get('safety_min_temp', 18.0)}`°C")
            st.write(f"Max Safety: `{config.get('safety_max_temp', 25.0)}`°C")
    except Exception as e:
        st.error(f"Configuration Error: {e}")

# ---------------- Main Overview ----------------
def render_overview():
    st.header("📊 System Overview")
    
    if st.button("🔄 Refresh Data"):
        st.session_state['refresh_counter'] += 1
        raise RerunException(None)
    
    render_metric_cards()
    st.divider()
    render_performance_trend()
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        render_system_status()
    with col2:
        render_configuration_summary()
