"""
ML Heating Dashboard - Performance Component
Real-time performance monitoring and analytics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from streamlit.runtime.scriptrunner import RerunException

# ---------------- Session State Initialization ----------------
if 'show_logs' not in st.session_state:
    st.session_state['show_logs'] = False
if 'lines_to_show' not in st.session_state:
    st.session_state['lines_to_show'] = 100

# ---------------- Log Data ----------------
def get_recent_performance_logs():
    try:
        log_file = '/data/logs/ml_heating.log'
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()[-st.session_state['lines_to_show']:]
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

# ---------------- Render Performance Chart ----------------
def render_performance():
    st.header("📈 System Performance")
    
    df = get_recent_performance_logs()
    
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
                       tickfont=dict(color="#1f77b4"), range=[0,1]),
            yaxis2=dict(title="MAE (°C)", title_font=dict(color="#ff7f0e"),
                        tickfont=dict(color="#ff7f0e"), overlaying="y", side="right",
                        range=[0, max(df['mae'])*1.2]),
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No performance data available yet.")

# ---------------- Log Viewer ----------------
def render_log_viewer():
    if st.session_state['show_logs']:
        st.subheader("📋 System Logs")
        
        log_files = {
            "ML Heating": "/data/logs/ml_heating.log",
            "Dashboard": "/data/logs/dashboard.log",
            "Health Check": "/data/logs/health_server.log",
            "Supervisor": "/data/logs/supervisord.log"
        }
        
        log_type = st.selectbox("Select log file:", list(log_files.keys()))
        log_file = log_files[log_type]
        
        st.session_state['lines_to_show'] = st.selectbox(
            "Lines to show:", [50, 100, 200, 500], index=[50,100,200,500].index(st.session_state['lines_to_show'])
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh Logs"):
                raise RerunException(None)
        with col2:
            if st.button("❌ Close Logs"):
                st.session_state['show_logs'] = False
                raise RerunException(None)
        
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()[-st.session_state['lines_to_show']:]
                st.text_area(f"Last {st.session_state['lines_to_show']} lines from {log_type}",
                             ''.join(lines), height=400, disabled=True)
            else:
                st.warning(f"Log file not found: {log_file}")
        except Exception as e:
            st.error(f"Error reading log file: {e}")

# ---------------- Main Render ----------------
def render_performance_page():
    render_performance()
    
    if st.session_state['show_logs']:
        st.divider()
        render_log_viewer()
