# ui_components.py

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def load_css():
    """Load custom CSS for futuristic styling"""
    try:
        with open('assets/style.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
            if css_content.strip():  # Only load if CSS file has content
                st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CSS file not found")
    except Exception as e:
        st.error(f"Error loading CSS: {e}")

def create_header():
    """Create the main header with futuristic styling"""
    st.markdown("""
        <div class="main-header">
            <h1>🏊‍♂️ AQUA SCHEDULER PRO</h1>
            <p style="text-align: center; margin: 0; font-size: 1.2rem; opacity: 0.8;">
                Intelligent Swim Lesson Scheduling System
            </p>
        </div>
    """, unsafe_allow_html=True)

def create_status_card(title, value, icon, color="#00d4ff"):
    """Create a status card with futuristic styling"""
    st.markdown(f"""
        <div class="futuristic-card neon-border">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h3 style="margin: 0; color: {color}; font-family: 'Orbitron', monospace;">{title}</h3>
                    <p style="margin: 0; font-size: 2rem; font-weight: bold; color: white;">{value}</p>
                </div>
                <div style="font-size: 3rem;">{icon}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def create_progress_dashboard(availability_df, template_df):
    """Create a progress dashboard with visual indicators"""
    if availability_df is not None and template_df is not None:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_status_card("Instructors", len(availability_df), "👥")
        
        with col2:
            total_classes = len(template_df.columns) - 1  # Exclude time column
            create_status_card("Classes", total_classes, "🏊‍♀️")
        
        with col3:
            # Calculate available hours safely
            total_hours = 0
            for _, row in availability_df.iterrows():
                start_time = row['AM Start']
                end_time = row['AM End']
                
                # Handle different time formats
                if hasattr(start_time, 'time'):
                    start_time = start_time.time()
                if hasattr(end_time, 'time'):
                    end_time = end_time.time()
                
                # Convert to datetime for calculation
                try:
                    start_dt = datetime.combine(datetime.today(), start_time)
                    end_dt = datetime.combine(datetime.today(), end_time)
                    hours = (end_dt - start_dt).total_seconds() / 3600
                    total_hours += hours
                except:
                    total_hours += 4  # Default 4 hours if conversion fails
            
            create_status_card("Total Hours", f"{total_hours:.1f}h", "⏰")
        
        with col4:
            coverage_ratio = len(availability_df) / max(1, total_classes)
            create_status_card("Coverage", f"{coverage_ratio:.1f}x", "📊")

def create_instructor_card(name, start_time, end_time, role, cant_teach=""):
    """Create an individual instructor card"""
    st.markdown(f"""
        <div class="futuristic-card" style="margin: 1rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: #00d4ff; font-family: 'Orbitron', monospace;">{name}</h4>
                    <p style="margin: 0.5rem 0; opacity: 0.8;">{start_time} - {end_time}</p>
                    <p style="margin: 0; font-size: 0.9rem; color: #00ff88;">Role: {role}</p>
                    {f'<p style="margin: 0; font-size: 0.8rem; color: #ff6b6b;">Can\'t teach: {cant_teach}</p>' if cant_teach else ''}
                </div>
                <div style="font-size: 2rem;">{'👨‍🏫' if role == 'Instructor' else '👥'}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def create_schedule_visualization(schedule_data):
    """Create a visual schedule heatmap"""
    if schedule_data is None:
        return
    
    # Convert schedule data to heatmap format
    df = pd.DataFrame(schedule_data)
    
    # Create heatmap
    fig = px.imshow(
        df.values,
        x=df.columns,
        y=df.index,
        color_continuous_scale='Blues',
        aspect='auto'
    )
    
    fig.update_layout(
        title="Schedule Heatmap",
        xaxis_title="Classes",
        yaxis_title="Time Slots",
        template="plotly_dark",
        font=dict(color="white")
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_availability_chart(availability_df):
    """Create a visual availability chart"""
    if availability_df is None or availability_df.empty:
        return
    
    # Create availability timeline
    fig = go.Figure()
    
    for _, row in availability_df.iterrows():
        # Fix datetime conversion - handle both time objects and datetime objects
        start_time = row['AM Start']
        end_time = row['AM End']
        
        # Convert to time if it's a datetime object
        if hasattr(start_time, 'time'):
            start_time = start_time.time()
        if hasattr(end_time, 'time'):
            end_time = end_time.time()
        
        # Convert to string for plotting if needed
        start_str = str(start_time) if start_time else "08:00"
        end_str = str(end_time) if end_time else "12:00"
        
        # Create a simple bar chart for availability
        fig.add_trace(go.Bar(
            name=row['Name'],
            x=[f"{start_str} - {end_str}"],
            y=[1],
            text=[row['Name']],
            textposition='auto',
            marker_color='rgba(0, 255, 255, 0.7)',
            hovertemplate=f"<b>{row['Name']}</b><br>Role: {row['Role']}<br>Available: {start_str} - {end_str}<extra></extra>"
        ))
    
    fig.update_layout(
        title="Instructor Availability",
        xaxis_title="Time Slots",
        yaxis_title="Availability",
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_loading_animation():
    """Create a loading animation"""
    st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <div class="pulse" style="font-size: 3rem;">⚡</div>
            <p style="margin-top: 1rem; color: #00d4ff;">Processing Schedule...</p>
        </div>
    """, unsafe_allow_html=True)

def create_success_message(message):
    """Create a success message with animation"""
    st.markdown(f"""
        <div class="futuristic-card glow" style="border-color: #00ff88;">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 2rem; margin-right: 1rem;">✅</div>
                <div>
                    <h4 style="margin: 0; color: #00ff88;">Success!</h4>
                    <p style="margin: 0.5rem 0 0 0;">{message}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def create_error_message(message):
    """Create an error message with styling"""
    st.markdown(f"""
        <div class="futuristic-card" style="border-color: #ff6b6b;">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 2rem; margin-right: 1rem;">❌</div>
                <div>
                    <h4 style="margin: 0; color: #ff6b6b;">Error</h4>
                    <p style="margin: 0.5rem 0 0 0;">{message}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def create_warning_message(message):
    """Create a warning message with styling"""
    st.markdown(f"""
        <div class="futuristic-card" style="border-color: #ffa500;">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 2rem; margin-right: 1rem;">⚠️</div>
                <div>
                    <h4 style="margin: 0; color: #ffa500;">Warning</h4>
                    <p style="margin: 0.5rem 0 0 0;">{message}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def create_navigation_tabs():
    """Create navigation tabs"""
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Schedule", "👥 Instructors", "📊 Analytics", "⚙️ Settings"])
    return tab1, tab2, tab3, tab4

def create_sidebar_menu():
    """Create sidebar menu with futuristic styling using radio buttons"""
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h3 style="color: #00d4ff; font-family: 'Orbitron', monospace;">NAVIGATION</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Use radio buttons for navigation to prevent rerun issues
    menu_options = {
        "🏠 Dashboard": "dashboard",
        "📅 Schedule Generator": "schedule",
        "👥 Instructor Management": "instructors",
        "🤖 AI Assistant": "ai_assistant",
        "📊 Analytics": "analytics",
        "⚙️ Settings": "settings",
        "❓ Help": "help"
    }
    
    # Initialize session state for navigation if not exists
    if 'current_nav' not in st.session_state:
        st.session_state.current_nav = "dashboard"
    
    # Create radio buttons for navigation
    selected = st.sidebar.radio(
        "Navigation",
        options=list(menu_options.keys()),
        index=list(menu_options.keys()).index([k for k, v in menu_options.items() if v == st.session_state.current_nav][0]),
        label_visibility="collapsed",
        key="nav_radio"
    )
    
    # Update session state
    st.session_state.current_nav = menu_options[selected]
    
    return st.session_state.current_nav

def create_footer():
    """Create a futuristic footer"""
    st.markdown("""
        <div style="text-align: center; padding: 2rem; margin-top: 3rem; border-top: 1px solid rgba(255,255,255,0.1);">
            <p style="color: rgba(255,255,255,0.6); margin: 0;">
                🚀 Powered by AI • Built with Streamlit • © 2024 Aqua Scheduler Pro
            </p>
        </div>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create a metric card with optional delta"""
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def create_timeline_chart(schedule_data):
    """Create a timeline chart of the schedule"""
    if schedule_data is None:
        return
    
    # Convert schedule data to timeline format
    timeline_data = []
    
    for time_idx, time_slot in enumerate(schedule_data.index):
        for class_idx, class_name in enumerate(schedule_data.columns):
            value = schedule_data.iloc[time_idx, class_idx]
            if pd.notna(value) and value != "":
                timeline_data.append({
                    'Time': time_slot,
                    'Class': class_name,
                    'Instructor': str(value),
                    'Time_Index': time_idx
                })
    
    if timeline_data:
        df_timeline = pd.DataFrame(timeline_data)
        
        fig = px.scatter(
            df_timeline,
            x='Time_Index',
            y='Class',
            color='Instructor',
            size=[10] * len(df_timeline),
            title="Schedule Timeline",
            template="plotly_dark"
        )
        
        fig.update_layout(
            font=dict(color="white"),
            xaxis_title="Time Slots",
            yaxis_title="Classes"
        )
        
        st.plotly_chart(fig, use_container_width=True) 