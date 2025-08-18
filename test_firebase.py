# test_firebase.py - Test Firebase connectivity

import streamlit as st
from firebase_config import firebase_manager

def test_firebase():
    st.title("Firebase Test")
    
    # Test basic connectivity
    st.write("Testing Firebase connectivity...")
    
    try:
        # Test user creation
        test_user_data = {
            "email": "test@example.com",
            "role": "supervisor",
            "created_at": "2024-01-01T00:00:00",
            "is_verified": True
        }
        
        # Test writing to users collection
        st.write("Testing user data write...")
        firebase_manager.db.collection("users").document("test_user").set(test_user_data)
        st.success("✅ User data written successfully!")
        
        # Test reading from users collection
        st.write("Testing user data read...")
        doc = firebase_manager.db.collection("users").document("test_user").get()
        if doc.exists:
            st.success("✅ User data read successfully!")
            st.write("Data:", doc.to_dict())
        else:
            st.error("❌ User data not found!")
            
        # Test instructor data
        st.write("Testing instructor data write...")
        test_instructor = {
            "name": "Test Instructor",
            "email": "instructor@test.com",
            "role": "instructor",
            "supervisor_id": "test_supervisor",
            "created_at": "2024-01-01T00:00:00"
        }
        
        result = firebase_manager.db.collection("instructors").add(test_instructor)
        st.success(f"✅ Instructor added with ID: {result[1].id}")
        
        # Test schedule data
        st.write("Testing schedule data write...")
        test_schedule = {
            "title": "Test Schedule",
            "supervisor_id": "test_supervisor",
            "posted_at": "2024-01-01T00:00:00",
            "is_active": True,
            "schedule_data": {"test": "data"}
        }
        
        result = firebase_manager.db.collection("schedules").add(test_schedule)
        st.success(f"✅ Schedule added with ID: {result[1].id}")
        
    except Exception as e:
        st.error(f"❌ Firebase test failed: {e}")
        st.write("Error details:", str(e))

if __name__ == "__main__":
    test_firebase()

