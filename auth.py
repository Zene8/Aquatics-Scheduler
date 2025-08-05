# auth.py - Enhanced Authentication System

import streamlit as st
from ui_components import load_css, create_header, create_success_message, create_error_message

def login_form():
    """Enhanced login form with futuristic styling"""
    load_css()
    
    # Create a centered login container
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; min-height: 100vh;">
            <div class="futuristic-card" style="width: 400px; text-align: center;">
                <div style="margin-bottom: 2rem;">
                    <h1 style="color: #00d4ff; font-family: 'Orbitron', monospace; margin-bottom: 0.5rem;">
                        🏊‍♂️ AQUA SCHEDULER PRO
                    </h1>
                    <p style="opacity: 0.8; margin: 0;">Intelligent Swim Lesson Scheduling for YMCA Sammamish Aquatics Center</p>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🔐</div>
                    <h3 style="color: #00d4ff; margin-bottom: 1rem;">Supervisor Login</h3>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Create login form
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🚀 Login", use_container_width=True)
        
        if submitted:
            if username == "admin" and password == "swim123":
                st.session_state.logged_in = True
                create_success_message("Login successful! Welcome to Aqua Scheduler Pro.")
                st.rerun()
            else:
                create_error_message("Invalid credentials. Please try again.")
    
    # Add demo credentials hint
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; opacity: 0.6;">
            <small>Demo Credentials: admin / swim123</small>
        </div>
    """, unsafe_allow_html=True)
    
    # Add system status
    st.markdown("""
        <div style="position: fixed; bottom: 20px; right: 20px; background: rgba(0,0,0,0.8); padding: 10px; border-radius: 10px; border: 1px solid #00d4ff;">
            <small style="color: #00d4ff;">🟢 System Online</small>
        </div>
    """, unsafe_allow_html=True)