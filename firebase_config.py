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
            print("🔍 Starting Firebase initialization...")
            
            # Validate Firebase configuration
            required_keys = ['apiKey', 'authDomain', 'databaseURL', 'projectId']
            missing_keys = [key for key in required_keys if not FIREBASE_CONFIG.get(key)]
            
            if missing_keys:
                error_msg = f"❌ Missing required Firebase configuration keys: {missing_keys}"
                if hasattr(st, 'error'):
                    st.error(error_msg)
                    st.stop()
                else:
                    raise Exception(error_msg)
            
            print("✅ Firebase configuration validation passed")
            
            # Validate database URL
            if not FIREBASE_CONFIG.get('databaseURL'):
                error_msg = "❌ Database URL is missing from Firebase configuration"
                if hasattr(st, 'error'):
                    st.error(error_msg)
                    st.stop()
                else:
                    raise Exception(error_msg)
            
            print(f"✅ Database URL validated: {FIREBASE_CONFIG.get('databaseURL')}")
            
            # Initialize Pyrebase for authentication
            print("🔍 Initializing Pyrebase...")
            import pyrebase
            self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
            self.auth = self.firebase.auth()
            print("✅ Pyrebase initialized successfully")
            
            # Initialize Firebase Admin SDK for database operations and auth verification
            print("🔍 Importing Firebase Admin SDK...")
            import firebase_admin
            from firebase_admin import credentials, db, auth as admin_auth
            print("✅ Firebase Admin SDK imported successfully")
            
            # Check if Firebase Admin is already initialized
            if not firebase_admin._apps:
                print("🔍 Firebase Admin not initialized, initializing now...")
                # Use service account credentials - try Streamlit secrets first, then local file
                cred = None
                try:
                    # Try to use Streamlit secrets (for deployment)
                    secrets_available = False
                    try:
                        if hasattr(st, 'secrets') and st.secrets is not None and 'firebase' in st.secrets:
                            secrets_available = True
                    except:
                        secrets_available = False
                    
                    if secrets_available:
                        print("🔍 Using Streamlit secrets for Firebase credentials...")
                        sa = dict(st.secrets["firebase"])
                        cred = credentials.Certificate(sa)
                        if hasattr(st, 'write'):
                            st.write("✅ Using Firebase credentials from Streamlit secrets")
                        else:
                            print("✅ Using Firebase credentials from Streamlit secrets")
                    else:
                        # Fall back to local file (for development)
                        print("🔍 Using local service account key file...")
                        try:
                            cred = credentials.Certificate("serviceAccountKey.json")
                            if hasattr(st, 'write'):
                                st.write("✅ Using Firebase credentials from local file")
                            else:
                                print("✅ Using Firebase credentials from local file")
                        except Exception as e:
                            print(f"❌ Failed to load service account key: {e}")
                            raise e
                except Exception as e:
                    print(f"❌ Failed to load Firebase credentials: {e}")
                    if hasattr(st, 'error'):
                        st.error(f"❌ Failed to load Firebase credentials: {e}")
                        st.error("For deployment: Add Firebase credentials to Streamlit secrets")
                        st.error("For development: Ensure serviceAccountKey.json is in the project directory")
                        st.stop()
                    else:
                        raise Exception(f"❌ Failed to load Firebase credentials: {e}")
                
                if cred is None:
                    raise Exception("No Firebase credentials loaded")
                
                print(f"🔍 Initializing Firebase Admin with database URL: {FIREBASE_CONFIG['databaseURL']}")
                try:
                    firebase_admin.initialize_app(cred, {
                        'databaseURL': FIREBASE_CONFIG['databaseURL']
                    })
                    print("✅ Firebase Admin app initialized")
                except Exception as e:
                    print(f"❌ Firebase Admin initialization failed: {e}")
                    raise e
            else:
                print("✅ Firebase Admin already initialized")
            
            self.admin_db = db.reference()
            self.admin_auth = admin_auth
            
            # Debug: Check if initialization was successful
            if self.admin_db is None:
                raise Exception("Firebase Admin SDK database reference is None")
            if self.admin_auth is None:
                raise Exception("Firebase Admin SDK auth reference is None")
                
            if hasattr(st, 'success'):
                st.success("✅ Firebase Admin SDK connected successfully!")
            else:
                print("✅ Firebase Admin SDK connected successfully!")
            
        except ImportError as e:
            error_msg = f"❌ Firebase libraries not installed. Please run: pip install firebase-admin pyrebase4"
            if hasattr(st, 'error'):
                st.error(error_msg)
                st.stop()
            else:
                raise Exception(error_msg)
        except FileNotFoundError:
            error_msg = "❌ serviceAccountKey.json not found. Please ensure the service account key file is in the project directory."
            if hasattr(st, 'error'):
                st.error(error_msg)
                st.stop()
            else:
                raise Exception(error_msg)
        except Exception as e:
            error_msg = f"❌ Firebase initialization failed: {e}"
            if hasattr(st, 'error'):
                st.error(error_msg)
                st.stop()
            else:
                raise Exception(error_msg)
    
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
    
    def _convert_time_objects(self, obj):
        """Convert datetime.time objects to strings for JSON serialization"""
        if isinstance(obj, dict):
            return {key: self._convert_time_objects(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_time_objects(item) for item in obj]
        elif hasattr(obj, 'strftime') and hasattr(obj, 'hour') and hasattr(obj, 'minute'):
            # This is a time object
            return obj.strftime("%H:%M")
        elif hasattr(obj, 'isoformat'):
            # This is a datetime object
            return obj.isoformat()
        else:
            return obj
    
    def _clean_data_for_firebase(self, data):
        """Clean data to ensure Firebase compatibility"""
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                # Firebase doesn't like certain characters in keys
                clean_key = str(key).replace('.', '_').replace('#', '_').replace('$', '_').replace('[', '_').replace(']', '_')
                
                if isinstance(value, dict):
                    cleaned[clean_key] = self._clean_data_for_firebase(value)
                elif isinstance(value, list):
                    cleaned[clean_key] = [self._clean_data_for_firebase(item) for item in value]
                elif value is None:
                    cleaned[clean_key] = ""  # Convert None to empty string
                elif value == "":
                    cleaned[clean_key] = " "  # Convert empty string to space
                else:
                    cleaned[clean_key] = str(value)  # Convert everything to string
            return cleaned
        elif isinstance(data, list):
            return [self._clean_data_for_firebase(item) for item in data]
        elif data is None:
            return ""
        elif data == "":
            return " "
        else:
            return str(data)
    
    def post_schedule(self, schedule_data, supervisor_id):
        """Post schedule to database and return instructor emails"""
        try:
            # Convert time objects to strings for JSON serialization
            serializable_data = self._convert_time_objects(schedule_data)
            
            serializable_data["supervisor_id"] = supervisor_id
            serializable_data["posted_at"] = datetime.now().isoformat()
            serializable_data["is_active"] = True
            
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
            serializable_data["instructor_emails"] = instructor_emails
            
            # Add to Realtime Database using Admin SDK
            try:
                # Debug: Print the data being sent to Firebase
                print(f"🔍 Posting schedule data with {len(serializable_data)} keys")
                print(f"🔍 Schedule data keys: {list(serializable_data.keys())}")
                if 'schedule_data' in serializable_data:
                    print(f"🔍 Schedule data rows: {len(serializable_data['schedule_data'])}")
                
                # Clean the data to ensure Firebase compatibility
                cleaned_data = self._clean_data_for_firebase(serializable_data)
                print(f"🔍 Data cleaned for Firebase compatibility")
                
                # Test the cleaned data
                import json
                try:
                    json.dumps(cleaned_data)
                    print("✅ Cleaned data is JSON serializable")
                except Exception as e:
                    print(f"❌ Cleaned data JSON error: {e}")
                    raise e
                
                self.admin_db.child("schedules").push(cleaned_data)
                return {"success": True, "instructor_emails": instructor_emails}
            except Exception as e:
                print(f"❌ Firebase push failed: {e}")
                # Try to identify the problematic data
                import json
                try:
                    json.dumps(serializable_data)
                    print("✅ Data is JSON serializable")
                except Exception as json_error:
                    print(f"❌ JSON serialization error: {json_error}")
                    # Try to find the problematic field
                    for key, value in serializable_data.items():
                        try:
                            json.dumps({key: value})
                        except:
                            print(f"❌ Problematic field: {key}")
                
                # Try to identify the issue by examining the data structure
                print("🔍 Examining schedule data structure...")
                if 'schedule_data' in serializable_data:
                    schedule_rows = serializable_data['schedule_data']
                    for i, row in enumerate(schedule_rows):
                        print(f"🔍 Row {i}: {list(row.keys())}")
                        for key, value in row.items():
                            if value is None or value == "":
                                print(f"⚠️ Empty value in row {i}, key '{key}': {repr(value)}")
                            elif isinstance(value, str) and len(value) > 100:
                                print(f"⚠️ Long string in row {i}, key '{key}': {len(value)} chars")
                
                raise e
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
