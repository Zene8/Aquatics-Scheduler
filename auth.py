# auth.py - Firebase Authentication System

import streamlit as st
from ui_components import load_css, create_header, create_success_message, create_error_message
from firebase_config import firebase_manager

def show_auth_page():
    """Show authentication page with sign up and sign in options"""
    load_css()
    
    # Create a clean authentication container
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; min-height: 80vh;">
            <div class="futuristic-card" style="width: 500px; text-align: center; padding: 2rem;">
                <h1 style="color: #00d4ff; font-family: 'Orbitron', monospace; margin-bottom: 1rem;">
                    🏊‍♂️ AQUA SCHEDULER PRO
                </h1>
                <p style="opacity: 0.8; margin-bottom: 2rem;">Intelligent Swim Lesson Scheduling for YMCA Sammamish Aquatics Center</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for sign in and sign up
    tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Sign Up"])
    
    with tab1:
        show_sign_in_form()
    
    with tab2:
        show_sign_up_form()

def show_sign_in_form():
    """Show sign in form"""
    st.markdown("### Sign In to Your Account")
    
    with st.form("sign_in_form", clear_on_submit=True):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)
        
        if submitted:
            if email and password:
                result = firebase_manager.sign_in(email, password)
                if result["success"]:
                    st.session_state.logged_in = True
                    st.session_state.user_data = result["user_data"]
                    st.session_state.user_role = result["role"]
                    st.session_state.user_id = result["user"]["localId"]
                    create_success_message("Sign in successful! Welcome back.")
                    st.rerun()
                else:
                    error_msg = result['error']
                    if "Email not verified" in error_msg:
                        create_error_message("⚠️ Email not verified. Please check your inbox and click the verification link before signing in.")
                        st.info("💡 **Tip**: If you don't see the email, check your spam folder.")
                    else:
                        create_error_message(f"Sign in failed: {error_msg}")
            else:
                create_error_message("Please enter both email and password.")

def show_sign_up_form():
    """Show sign up form"""
    st.markdown("### Create New Account")
    
    with st.form("sign_up_form", clear_on_submit=True):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        role = st.selectbox("Role", ["employee", "supervisor"], help="Select your role in the organization")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("📝 Create Account", use_container_width=True)
        
        if submitted:
            if not email or not password or not confirm_password:
                create_error_message("Please fill in all fields.")
            elif password != confirm_password:
                create_error_message("Passwords do not match.")
            elif len(password) < 6:
                create_error_message("Password must be at least 6 characters long.")
            else:
                result = firebase_manager.sign_up(email, password, role)
                if result["success"]:
                    create_success_message("✅ Account created successfully! Please check your email for verification.")
                    st.info("📧 **Verification Email Sent**: Check your inbox (and spam folder) for a verification link. Click the link to verify your account before signing in.")
                else:
                    create_error_message(f"Sign up failed: {result['error']}")

def check_auth():
    """Check if user is authenticated"""
    if not st.session_state.get('logged_in', False):
        show_auth_page()
        st.stop()
    
    return st.session_state.get('user_role', 'employee')

def get_user_role():
    """Get current user's role"""
    return st.session_state.get('user_role', 'employee')

def is_supervisor():
    """Check if current user is a supervisor"""
    return get_user_role() == 'supervisor'

def logout():
    """Logout user"""
    for key in ['logged_in', 'user_data', 'user_role', 'user_id']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()