# test_simple.py - Simple Firebase test

import streamlit as st
from firebase_config import firebase_manager

def test_firebase():
    st.title("Simple Firebase Test")
    
    st.write("Testing Firebase connectivity...")
    
    try:
        # Test writing to users collection
        test_data = {
            "email": "test@example.com",
            "role": "supervisor",
            "created_at": "2024-01-01T00:00:00",
            "is_verified": True
        }
        
        firebase_manager.db.collection("users").document("test_user").set(test_data)
        st.success("✅ Data written to Firestore successfully!")
        
        # Test reading from users collection
        doc = firebase_manager.db.collection("users").document("test_user").get()
        if doc.exists:
            st.success("✅ Data read from Firestore successfully!")
            st.write("Data:", doc.to_dict())
        else:
            st.error("❌ Data not found!")
            
    except Exception as e:
        st.error(f"❌ Test failed: {e}")
        st.write("Error details:", str(e))

if __name__ == "__main__":
    test_firebase()

