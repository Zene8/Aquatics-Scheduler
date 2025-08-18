# test_firebase_simple.py - Simple Firebase Realtime Database test

import streamlit as st
from firebase_config import firebase_manager

def test_firebase():
    st.title("Firebase Realtime Database Test")
    
    st.write("Testing Firebase connectivity...")
    
    try:
        # Test writing to users collection
        test_data = {
            "email": "test@example.com",
            "role": "supervisor",
            "created_at": "2024-01-01T00:00:00",
            "is_verified": True
        }
        
        firebase_manager.db.child("users").child("test_user").set(test_data)
        st.success("✅ Data written to Firebase Realtime Database successfully!")
        
        # Test reading from users collection
        data = firebase_manager.db.child("users").child("test_user").get().val()
        if data:
            st.success("✅ Data read from Firebase Realtime Database successfully!")
            st.write("Data:", data)
        else:
            st.error("❌ Data not found!")
            
    except Exception as e:
        st.error(f"❌ Test failed: {e}")
        st.write("Error details:", str(e))

if __name__ == "__main__":
    test_firebase()

