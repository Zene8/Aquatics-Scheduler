# config.py - Application Configuration

import os
from datetime import time

# App Configuration
APP_NAME = "Aqua Scheduler Pro"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Intelligent Swim Lesson Scheduling System"

# Authentication
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "swim123"

# Default Instructor Credentials (for future use)
INSTRUCTOR_CREDENTIALS = {
    "sarah": "sarah123",
    "mike": "mike123", 
    "emma": "emma123",
    "alex": "alex123"
}

# Time Settings
DEFAULT_START_TIME = time(8, 0)  # 8:00 AM
DEFAULT_END_TIME = time(12, 0)   # 12:00 PM

# Schedule Settings
MAX_INSTRUCTORS = 20
MAX_CLASSES = 50
MIN_BREAK_TIME = 15  # minutes

# File Paths
ASSETS_DIR = "assets"
TEMPLATES_DIR = "templates"
OUTPUT_DIR = "output"

# UI Colors
PRIMARY_COLOR = "#00d4ff"
SECONDARY_COLOR = "#0099cc"
SUCCESS_COLOR = "#00ff88"
WARNING_COLOR = "#ffa500"
ERROR_COLOR = "#ff6b6b"

# Animation Settings
ANIMATION_DURATION = 0.3
PULSE_INTERVAL = 2.0

# Email Settings (for future use)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_FROM = "noreply@aquascheduler.com"

# Database Settings (for future use)
DATABASE_URL = "sqlite:///aqua_scheduler.db"

# AI Settings (for future use)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = "gpt-4"

# Notification Settings
ENABLE_EMAIL_NOTIFICATIONS = True
ENABLE_SCHEDULE_REMINDERS = True
REMINDER_TIME = time(7, 30)  # 7:30 AM

# Export Settings
DEFAULT_EXPORT_FORMAT = "xlsx"
INCLUDE_TIMESTAMP = True
AUTO_SAVE = True

# Performance Settings
CACHE_TTL = 3600  # 1 hour
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ENABLE_COMPRESSION = True

# Security Settings
SESSION_TIMEOUT = 3600  # 1 hour
MAX_LOGIN_ATTEMPTS = 3
PASSWORD_MIN_LENGTH = 8

# Feature Flags
ENABLE_AI_SCHEDULING = True
ENABLE_ANALYTICS = True
ENABLE_INSTRUCTOR_PORTAL = False  # Future feature
ENABLE_MOBILE_APP = False  # Future feature
ENABLE_API_ACCESS = False  # Future feature

# Default Templates
DEFAULT_TEMPLATE_NAMES = [
    "Monday_Template.xlsx",
    "Tuesday_Template.xlsx", 
    "Wednesday_Template.xlsx",
    "Thursday_Template.xlsx",
    "Friday_Template.xlsx"
]

# Class Types
CLASS_TYPES = [
    "Beginner",
    "Intermediate", 
    "Advanced",
    "Private",
    "Group",
    "PSL"
]

# Instructor Roles
INSTRUCTOR_ROLES = [
    "Instructor",
    "Shadow",
    "Lead Instructor",
    "Assistant"
]

# Time Slots
DEFAULT_TIME_SLOTS = [
    "8:00 AM",
    "8:30 AM", 
    "9:00 AM",
    "9:30 AM",
    "10:00 AM",
    "10:30 AM",
    "11:00 AM",
    "11:30 AM",
    "12:00 PM"
]

# Validation Rules
MIN_STUDENTS_PER_CLASS = 1
MAX_STUDENTS_PER_CLASS = 8
MIN_INSTRUCTORS_PER_CLASS = 1
MAX_INSTRUCTORS_PER_CLASS = 2

# Error Messages
ERROR_MESSAGES = {
    "invalid_credentials": "Invalid username or password. Please try again.",
    "file_upload_error": "Error uploading file. Please check the format and try again.",
    "schedule_generation_error": "Error generating schedule. Please check instructor availability.",
    "template_parse_error": "Error parsing template. Please check the file format.",
    "insufficient_coverage": "Insufficient instructor coverage for all classes.",
    "time_conflict": "Time conflict detected. Please check instructor availability.",
    "file_not_found": "Template file not found. Please upload a valid template."
}

# Success Messages
SUCCESS_MESSAGES = {
    "login_success": "Login successful! Welcome to Aqua Scheduler Pro.",
    "template_uploaded": "Template uploaded successfully!",
    "schedule_generated": "Schedule generated successfully!",
    "instructor_added": "Instructor added successfully!",
    "settings_saved": "Settings saved successfully!",
    "file_downloaded": "File downloaded successfully!"
}

# Help Content
HELP_CONTENT = {
    "getting_started": """
    ## Getting Started
    
    1. **Upload Template**: Start by uploading your Excel template or manually selecting classes
    2. **Add Instructors**: Enter instructor details including availability and preferences  
    3. **Generate Schedule**: Let the AI create an optimized schedule
    4. **Download**: Get your final schedule in Excel format
    """,
    
    "interface_guide": """
    ## Interface Guide
    
    - **Dashboard**: Overview of your scheduling system
    - **Schedule Generator**: Create new schedules step by step
    - **Instructor Management**: Add and manage instructor profiles
    - **Analytics**: View performance metrics and insights
    """,
    
    "troubleshooting": """
    ## Troubleshooting
    
    **Common Issues:**
    - Template not uploading: Ensure file is in .xlsx format
    - Schedule generation fails: Check instructor availability
    - Download issues: Clear browser cache and try again
    """
} 