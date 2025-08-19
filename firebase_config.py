# firebase_config.py - Firebase Admin SDK configuration

import streamlit as st
from datetime import datetime
import json
import os

# Firebase configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAquePMN_ExJ-WsFwKTzZ3Uc_1jnAsZn4M",
    "authDomain": "aqua-scheduler-pro.firebaseapp.com",
    "databaseURL": "https://aqua-scheduler-pro-default-rtdb.firebaseio.com",
    "projectId": "aqua-scheduler-pro",
    "storageBucket": "aqua-scheduler-pro.firebasestorage.app",
    "messagingSenderId": "808505694257",
    "appId": "1:808505694257:web:d91a2986f0da20c9891d10",
    "measurementId": "G-HZNX6HVBGZ"
}

# Firebase configuration loaded successfully

class FirebaseManager:
    def __init__(self):
        self.auth = None
        self.db = None
        self.admin_db = None
        self.admin_auth = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        try:
            # Validate Firebase configuration
            required_keys = ['apiKey', 'authDomain', 'databaseURL', 'projectId']
            missing_keys = [key for key in required_keys if not FIREBASE_CONFIG.get(key)]
            
            if missing_keys:
                st.error(f"❌ Missing required Firebase configuration keys: {missing_keys}")
                st.stop()
            
            # Validate database URL
            if not FIREBASE_CONFIG.get('databaseURL'):
                st.error("❌ Database URL is missing from Firebase configuration")
                st.stop()
            
            # Initialize Pyrebase for authentication
            import pyrebase
            self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
            self.auth = self.firebase.auth()
            
            # Initialize Firebase Admin SDK for database operations and auth verification
            import firebase_admin
            from firebase_admin import credentials, db, auth as admin_auth
            
            # Check if Firebase Admin is already initialized
            if not firebase_admin._apps:
                # Use service account credentials - try Streamlit secrets first, then local file
                try:
                    # Try to use Streamlit secrets (for deployment)
                    if hasattr(st, 'secrets') and 'firebase' in st.secrets:
                        sa = dict(st.secrets["firebase"])
                        cred = credentials.Certificate(sa)
                        st.write("✅ Using Firebase credentials from Streamlit secrets")
                    else:
                        # Fall back to local file (for development)
                        cred = credentials.Certificate("serviceAccountKey.json")
                        st.write("✅ Using Firebase credentials from local file")
                except Exception as e:
                    st.error(f"❌ Failed to load Firebase credentials: {e}")
                    st.error("For deployment: Add Firebase credentials to Streamlit secrets")
                    st.error("For development: Ensure serviceAccountKey.json is in the project directory")
                    st.stop()
                
                firebase_admin.initialize_app(cred, {
                    'databaseURL': FIREBASE_CONFIG['databaseURL']
                })
            
            self.admin_db = db.reference()
            self.admin_auth = admin_auth
            st.success("✅ Firebase Admin SDK connected successfully!")
            
        except ImportError as e:
            st.error(f"❌ Firebase libraries not installed. Please run: pip install firebase-admin pyrebase4")
            st.stop()
        except FileNotFoundError:
            st.error("❌ serviceAccountKey.json not found. Please ensure the service account key file is in the project directory.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Firebase initialization failed: {e}")
            st.stop()
    
    def sign_up(self, email, password, role):
        """Create user account with email verification"""
        try:
            # Create user in Firebase Auth using Pyrebase
            user = self.auth.create_user_with_email_and_password(email, password)
            
            # Send email verification
            self.auth.send_email_verification(user['idToken'])
            
            # Store user data in Realtime Database using Admin SDK
            user_data = {
                "email": email,
                "role": role,
                "created_at": datetime.now().isoformat(),
                "is_verified": False
            }
            
            self.admin_db.child("users").child(user['localId']).set(user_data)
            st.success("✅ User created successfully! Please check your email for verification.")
            
            return {"success": True, "user": user}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sign_in(self, email, password):
        """Sign in user with proper email verification check"""
        try:
            # Sign in with Firebase Auth using Pyrebase
            user = self.auth.sign_in_with_email_and_password(email, password)
            
            # Check email verification status using Admin SDK
            try:
                admin_user = self.admin_auth.get_user_by_email(email)
                email_verified = admin_user.email_verified
            except Exception as e:
                if "Invalid JWT Signature" in str(e) or "invalid_grant" in str(e):
                    st.warning("⚠️ JWT signature error - this may be due to service account key issues or time synchronization. Proceeding with sign-in...")
                else:
                    st.warning(f"⚠️ Could not verify email status: {e}")
                email_verified = True  # Allow sign-in if we can't verify status
            
            if not email_verified:
                st.warning("⚠️ Please verify your email before signing in. Check your inbox for a verification link.")
                return {"success": False, "error": "Email not verified"}
            
            # Get user data from Realtime Database using Admin SDK
            user_data = self.admin_db.child("users").child(user['localId']).get()
            
            if not user_data:
                # Create user data if it doesn't exist
                user_data = {
                    "email": email,
                    "role": "employee",
                    "created_at": datetime.now().isoformat(),
                    "is_verified": True
                }
                self.admin_db.child("users").child(user['localId']).set(user_data)
            
            # Update verification status in database
            user_data["is_verified"] = True
            self.admin_db.child("users").child(user['localId']).update({"is_verified": True})
            
            return {
                "success": True,
                "user": user,
                "user_data": user_data,
                "role": user_data.get("role", "employee")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_instructor(self, instructor_data, supervisor_id):
        """Add instructor to database"""
        try:
            instructor_data["supervisor_id"] = supervisor_id
            instructor_data["created_at"] = datetime.now().isoformat()
            
            # Add to Realtime Database using Admin SDK
            self.admin_db.child("instructors").push(instructor_data)
            return True
        except Exception as e:
            st.error(f"Failed to add instructor: {e}")
            return False
    
    def get_instructors(self, supervisor_id=None):
        """Get instructors from database - using simple query to avoid indexing issues"""
        try:
            # Get all instructors first
            all_instructors = self.admin_db.child("instructors").get()
            
            if not all_instructors:
                return {}
            
            # Filter by supervisor_id if provided
            if supervisor_id:
                filtered_instructors = {}
                for instructor_id, instructor_data in all_instructors.items():
                    if instructor_data.get("supervisor_id") == supervisor_id:
                        filtered_instructors[instructor_id] = instructor_data
                return filtered_instructors
            else:
                return all_instructors
                
        except Exception as e:
            st.error(f"Failed to get instructors: {e}")
            return {}
    
    def update_instructor(self, instructor_id, data):
        """Update instructor data"""
        try:
            self.admin_db.child("instructors").child(instructor_id).update(data)
            return True
        except Exception as e:
            st.error(f"Failed to update instructor: {e}")
            return False
    
    def delete_instructor(self, instructor_id):
        """Delete instructor"""
        try:
            self.admin_db.child("instructors").child(instructor_id).delete()
            return True
        except Exception as e:
            st.error(f"Failed to delete instructor: {e}")
            return False
    
    def post_schedule(self, schedule_data, supervisor_id):
        """Post schedule to database and return instructor emails"""
        try:
            schedule_data["supervisor_id"] = supervisor_id
            schedule_data["posted_at"] = datetime.now().isoformat()
            schedule_data["is_active"] = True
            
            # Get all instructor emails for this supervisor
            instructor_emails = []
            all_instructors = self.admin_db.child("instructors").get()
            
            if all_instructors:
                for instructor_id, instructor_data in all_instructors.items():
                    if instructor_data.get("supervisor_id") == supervisor_id:
                        instructor_email = instructor_data.get("email")
                        if instructor_email:
                            instructor_emails.append(instructor_email)
            
            # Add instructor emails to schedule data
            schedule_data["instructor_emails"] = instructor_emails
            
            # Add to Realtime Database using Admin SDK
            self.admin_db.child("schedules").push(schedule_data)
            return {"success": True, "instructor_emails": instructor_emails}
        except Exception as e:
            st.error(f"Failed to post schedule: {e}")
            return {"success": False, "error": str(e)}
    
    def get_active_schedule(self, user_email=None):
        """Get the most recent active schedule"""
        try:
            # Get all schedules first
            all_schedules = self.admin_db.child("schedules").get()
            
            if not all_schedules:
                return None
            
            # Filter active schedules and find the most recent
            latest_schedule = None
            latest_time = None
            
            for schedule_id, schedule_data in all_schedules.items():
                if schedule_data.get("is_active", False):
                    posted_time = schedule_data.get("posted_at", "")
                    if not latest_time or posted_time > latest_time:
                        latest_time = posted_time
                        latest_schedule = {"id": schedule_id, **schedule_data}
            
            # If user_email provided, check if they're an instructor for this supervisor
            if user_email and latest_schedule:
                supervisor_id = latest_schedule.get("supervisor_id")
                if supervisor_id:
                    # Get all instructors and filter by supervisor_id
                    all_instructors = self.admin_db.child("instructors").get()
                    
                    instructor_found = False
                    if all_instructors:
                        for instructor_id, instructor_data in all_instructors.items():
                            if instructor_data.get("supervisor_id") == supervisor_id:
                                instructor_email = instructor_data.get("email")
                                if instructor_email and instructor_email.lower() == user_email.lower():
                                    instructor_found = True
                                    break
                    
                    if not instructor_found:
                        return None  # User not authorized to see this schedule
            
            return latest_schedule
        except Exception as e:
            st.error(f"Failed to get active schedule: {e}")
            return None

# Initialize Firebase manager
firebase_manager = FirebaseManager()
