# Firebase Database Rules Setup Guide

## Current Issues Fixed:
✅ **Email Verification**: Now sends verification emails on signup
✅ **Database Indexing**: Fixed by using simple queries instead of complex indexing
✅ **Instructor Management**: Should now display instructors properly

## Firebase Console Setup:

### 1. Enable Email/Password Authentication:
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `aqua-scheduler-pro`
3. Click **"Authentication"** in left sidebar
4. Go to **"Sign-in method"** tab
5. Find **"Email/Password"** and click on it
6. Toggle to **"Enabled"**
7. Save changes

### 2. Database Rules (Optional - for better security):
Go to **Realtime Database** → **Rules** tab and use these rules:

```json
{
  "rules": {
    "users": {
      "$uid": {
        ".read": "$uid === auth.uid",
        ".write": "$uid === auth.uid"
      }
    },
    "instructors": {
      ".read": "auth != null",
      ".write": "auth != null"
    },
    "schedules": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}
```

## What's Fixed:

### ✅ Email Verification:
- Users now receive verification emails when they sign up
- Users must verify email before they can sign in
- Prevents unauthorized email usage

### ✅ Database Indexing:
- Removed complex queries that required indexing
- Now uses simple `get()` and filters in Python
- No more "Index not defined" errors

### ✅ Instructor Management:
- Instructors should now display properly
- Add/Edit/Delete functionality working
- Email field properly saved

## Test the App:
1. **Sign up** as a supervisor (check email for verification)
2. **Verify email** by clicking the link
3. **Sign in** with verified email
4. **Add instructors** - they should now appear in the list
5. **Post schedules** - should work without errors

The app should now work completely with proper Firebase Admin SDK integration! 🎉
