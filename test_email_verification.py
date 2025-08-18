# test_email_verification.py - Test email verification status

import firebase_admin
from firebase_admin import credentials, auth

def test_email_verification(email):
    """Test if a user's email is verified"""
    try:
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        
        # Get user by email
        user = auth.get_user_by_email(email)
        
        print(f"User ID: {user.uid}")
        print(f"Email: {user.email}")
        print(f"Email Verified: {user.email_verified}")
        print(f"Account Created: {user.user_metadata.creation_timestamp}")
        
        return user.email_verified
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Test with your email
    email = input("Enter email to test: ")
    is_verified = test_email_verification(email)
    
    if is_verified:
        print("✅ Email is verified!")
    else:
        print("❌ Email is not verified")
        print("Please check your email and click the verification link.")
