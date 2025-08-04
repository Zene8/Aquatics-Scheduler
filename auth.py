# auth.py
import streamlit as st

def login_form():
    st.title("🔐 Supervisor Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username == "admin" and password == "swim123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials. Try again.")