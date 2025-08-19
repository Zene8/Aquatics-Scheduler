# app.py - Futuristic Swim Scheduler

import streamlit as st
from scheduler import generate_am_schedule
from template_parser import parse_template
from ui_components import *

import pandas as pd
import io
import tempfile
from datetime import datetime, time
import os
from openpyxl import load_workbook, Workbook, styles
from shutil import copyfile
from ai_assistant import ai_assistant
from enrollment_parser import EnrollmentParser
# Initialize Firebase Admin exactly once, using the TOML section [firebase]
if not firebase_admin._apps:
    sa = dict(st.secrets["firebase"])  # section name must match your secrets TOML: [firebase]
    # DO NOT replace \\n here because your TOML uses triple quotes with real newlines
    cred = credentials.Certificate(sa)
    firebase_admin.initialize_app(cred)

# Optional: sanity logs to confirm the server is using the expected project
st.write("Admin project_id:", st.secrets["firebase"]["project_id"])
st.write("Admin client_email:", st.secrets["firebase"]["client_email"])
# Page Configuration
st.set_page_config(
    page_title="Aqua Scheduler Pro",
    page_icon="🏊‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# --- Session State Management --- #
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

if 'schedule_generated' not in st.session_state:
    st.session_state.schedule_generated = False

# --- Main Application --- #
def main():
    # Import auth functions here to avoid circular imports
    from auth import check_auth, get_user_role, is_supervisor, logout
    
    # Check authentication
    user_role = check_auth()
    
    # Create header
    create_header()
    
    # Create sidebar navigation
    current_section = create_sidebar_menu()
    
    # Main content based on navigation and user role
    if current_section == "dashboard":
        if user_role == 'supervisor':
            show_dashboard()
        else:
            show_employee_dashboard()
    elif current_section == "schedule":
        if user_role == 'supervisor':
            show_schedule_generator()
        else:
            show_employee_schedule_view()
    elif current_section == "instructors" and user_role == 'supervisor':
        show_instructor_management()
    elif current_section == "ai_assistant" and user_role == 'supervisor':
        show_ai_assistant()
    elif current_section == "analytics" and user_role == 'supervisor':
        show_analytics()
    elif current_section == "settings" and user_role == 'supervisor':
        show_settings()
    elif current_section == "help" and user_role == 'supervisor':
        show_help()
    
    # Create footer
    create_footer()

def show_dashboard():
    """Show the main dashboard with overview and quick actions"""
    st.markdown("## 📊 Dashboard Overview")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_metric_card("Active Instructors", "12", "+2", "normal")
    
    with col2:
        create_metric_card("Classes Today", "24", "-3", "inverse")
    
    with col3:
        create_metric_card("Coverage Rate", "94%", "+5%", "normal")
    
    # Recent activity
    st.markdown("### 🚀 Recent Activity")
    
    activity_data = [
        {"Time": "09:30", "Action": "Schedule Generated", "User": "Admin", "Status": "✅"},
        {"Time": "08:45", "Action": "Instructor Added", "User": "Admin", "Status": "✅"},
        {"Time": "08:15", "Action": "Template Uploaded", "User": "Admin", "Status": "✅"},
    ]
    
    for activity in activity_data:
        st.markdown(f"""
            <div class="futuristic-card" style="margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{activity['Action']}</strong>
                        <br><small style="opacity: 0.7;">{activity['Time']} • {activity['User']}</small>
                    </div>
                    <div style="font-size: 1.5rem;">{activity['Status']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📅 Generate New Schedule", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        if st.button("👥 Manage Instructors", use_container_width=True):
            st.session_state.current_section = "instructors"
            st.rerun()
    
    with col3:
        if st.button("📤 Post Schedule", use_container_width=True):
            st.markdown("### 📤 Post Schedule")
            uploaded_schedule = st.file_uploader(
                "Upload Excel Schedule to Post",
                type=["xlsx"],
                help="Upload a schedule file to post for instructors"
            )
            if uploaded_schedule and st.button("📤 Post Schedule", type="primary"):
                # TODO: Implement Firebase posting
                st.success("✅ Schedule posted successfully! Instructors can now view it.")
    
    with col4:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_section = "analytics"
            st.rerun()

def show_schedule_generator():
    """Show the schedule generator with enhanced UI"""
    st.markdown("## 📅 Schedule Generator")
    
    # Progress indicator
    steps = ["1. Upload Template", "2. Add Instructors", "3. Generate Schedule", "4. Download"]
    current_step = st.session_state.current_step
    
    # Progress bar
    progress = current_step / len(steps)
    st.progress(progress)
    
    # Step indicator
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        with cols[i]:
            if i + 1 <= current_step:
                st.markdown(f"<div style='text-align: center; color: #00d4ff; font-weight: bold;'>{step}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: center; opacity: 0.5;'>{step}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Step 1: Template Upload
    if current_step == 1:
        st.markdown("### 📋 Step 1: Upload Template")
        
        # Show contextual help
        help_tip = ai_assistant.get_help_tip("template_upload")
        st.info(help_tip)
        
        # Only reset template_generated flag when starting fresh (not when coming from manual selection)
        if 'template_generated' in st.session_state and not st.session_state.get('manual_mode', False):
            del st.session_state['template_generated']
        
        method = st.radio(
            "Choose Input Method",
            ["Upload Enrollments XCEL 🏆", "Upload Template", "Select Classes Manually"],
            horizontal=True
        )

        if method == "Upload Enrollments XCEL 🏆":
            st.markdown("### 📊 Upload Enrollment Data")
            st.markdown("**Recommended Method**: Upload enrollment Excel files to automatically generate your schedule template.")
            
            # Show contextual help
            help_tip = ai_assistant.get_help_tip("enrollment_upload")
            st.info(help_tip)
            
            # Date and session selection
            schedule_date = st.date_input("Select Schedule Date", value=datetime.now().date())
            session_mode = st.radio("Session Mode", ["AM", "PM"], horizontal=True, help="AM: 8:35-12:10, PM: 4:10-7:05")
            
            # Debug: Show what date is actually selected
            st.write(f"🔍 Selected Date: {schedule_date} ({schedule_date.strftime('%A')})")
            
            # Clear enrollment data if date or session mode changes
            current_key = f"{schedule_date}_{session_mode}"
            if 'last_enrollment_key' not in st.session_state or st.session_state['last_enrollment_key'] != current_key:
                st.session_state['enrollment_data'] = None
                st.session_state['am_template_df'] = None
                st.session_state['template_generated'] = False
                st.session_state['last_enrollment_key'] = current_key
            
            st.session_state['session_mode'] = session_mode
            
            # File uploads
            st.markdown("#### 📁 Upload Enrollment Files")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Group Lessons** (Required)")
                group_file = st.file_uploader(
                    "Upload Group Lessons Excel",
                    type=["xlsx"],
                    key="group_lessons",
                    help="Upload the group lessons enrollment file"
                )
            
            with col2:
                st.markdown("**Private Lessons** (Required)")
                private_file = st.file_uploader(
                    "Upload Private Lessons Excel", 
                    type=["xlsx"],
                    key="private_lessons",
                    help="Upload the private lessons enrollment file"
                )
            
            # Process files when both are uploaded
            if group_file and private_file:
                # Add clear cache button
                col1, col2 = st.columns([3, 1])
                with col1:
                    generate_button = st.button("🚀 Generate Schedule from Enrollments", type="primary")
                with col2:
                    if st.button("🔄 Clear Cache", help="Clear cached data and force fresh parsing"):
                        st.session_state['enrollment_data'] = None
                        st.session_state['am_template_df'] = None
                        st.session_state['template_generated'] = False
                        st.session_state['last_enrollment_key'] = None
                        st.rerun()
                
                if generate_button:
                    with st.spinner("Processing enrollment data..."):
                        try:
                            # Initialize parser
                            parser = EnrollmentParser()
                            
                            # Save uploaded files temporarily
                            group_path = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                            group_path.write(group_file.read())
                            group_path.close()
                            
                            private_path = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                            private_path.write(private_file.read())
                            private_path.close()
                            
                            print(f"🔍 Parsing for date: {schedule_date} ({schedule_date.strftime('%A')}) in {session_mode} mode")
                            print(f"🔍 Date type: {type(schedule_date)}")
                            print(f"🔍 Date value: {schedule_date}")
                            
                            # Parse enrollment data
                            group_classes = parser.parse_group_lessons(group_path.name, schedule_date, session_mode)
                            private_lessons = parser.parse_private_lessons(private_path.name, schedule_date, session_mode)
                            
                            # Generate template
                            success = parser.generate_schedule_template(group_classes, private_lessons, session_mode)
                            
                            if success:
                                # Store data for next steps
                                st.session_state['enrollment_data'] = {
                                    'group_classes': group_classes,
                                    'private_lessons': private_lessons,
                                    'schedule_date': schedule_date,
                                    'session_mode': session_mode
                                }
                                
                                # Generate preview
                                preview_df = parser.get_template_preview(group_classes, private_lessons, session_mode, schedule_date)
                                st.session_state['am_template_df'] = preview_df
                                
                                # Set template generated flag for enrollment mode
                                st.session_state['template_generated'] = True
                                st.session_state['enrollment_mode'] = True
                                st.session_state['am_template_file'] = "assets/Blank_MTWT_Template1.xlsx"
                                
                                create_success_message(f"Schedule template generated successfully for {schedule_date.strftime('%A, %B %d, %Y')}!")
                                
                                # Show preview with title
                                if hasattr(preview_df, 'attrs') and 'title' in preview_df.attrs:
                                    st.markdown(f"#### 📋 {preview_df.attrs['title']}")
                                else:
                                    st.markdown("#### 📋 Generated Schedule Preview")
                                st.dataframe(preview_df, height=300)
                                
                                # Show summary
                                st.markdown("#### 📊 Summary")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Group Classes", len(group_classes))
                                with col2:
                                    st.metric("Private Lessons", len(private_lessons))
                                with col3:
                                    st.metric("Total Students", sum(c['enrollment'] for c in group_classes) + len(private_lessons))
                                
                                # Show continue button only if template was generated
                                if st.session_state.get('template_generated', False):
                                    if st.button("Continue to Step 2", type="primary"):
                                        # Clear the template_generated flag to prevent issues
                                        st.session_state['template_generated'] = False
                                        st.session_state.current_step = 2
                                        st.rerun()
                            else:
                                create_error_message("Failed to generate schedule template. Please check your files and try again.")
                                
                        except Exception as e:
                            create_error_message(f"Error processing enrollment data: {str(e)}")
                            st.error(f"Technical details: {str(e)}")
            
            # Clean up temporary files
            elif group_file or private_file:
                st.warning("Please upload both group lessons and private lessons files to proceed.")

        elif method == "Upload Template":
            # Add session mode selection for template mode too
            session_mode = st.radio(
                "Session Mode",
                ["AM", "PM"],
                horizontal=True,
                help="AM: 8:35-12:10, PM: 4:10-7:05"
            )
            
            # Store session mode for use in instructor management
            st.session_state['session_mode'] = session_mode
            
            uploaded_file = st.file_uploader(
                f"Upload {session_mode} Session Template",
                type=["xlsx"],
                help="Upload your Excel template file"
            )
            
            if uploaded_file:
                with st.spinner("Processing template..."):
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                    tmp.write(uploaded_file.read())
                    tmp.flush()
                    tmp.close()
                    st.session_state['am_template_file'] = tmp.name
                    st.session_state['am_template_df'] = parse_template(tmp.name)

                    create_success_message("Template uploaded successfully!")
                    st.dataframe(st.session_state['am_template_df'], height=300)
                                
                    if st.button("Continue to Step 2", type="primary"):
                        st.session_state.current_step = 2
                        st.rerun()

        elif method == "Select Classes Manually":
            st.markdown("### Manually Select Classes")
            
            # Show contextual help for manual mode
            help_tip = ai_assistant.get_help_tip("manual_selection")
            st.info(help_tip)
            
            # AM/PM Mode Selection
            session_mode = st.radio(
                "Session Mode",
                ["AM", "PM"],
                horizontal=True,
                help="AM: 8:35-12:10, PM: 4:10-7:05"
            )
            
            # Store session mode for use in instructor management
            st.session_state['session_mode'] = session_mode
            
            # Create manual selection interface
            blank_template_path = os.path.join("assets", "Blank_MTWT_Template1.xlsx")
            if os.path.exists(blank_template_path):
                # Use the actual template file directly instead of creating a copy
                blank_df = pd.read_excel(blank_template_path, engine="openpyxl")
                
                # Update time slots based on session mode
                if session_mode == "AM":
                    am_times = ["8:35", "9:10", "9:45", "10:20", "11:00", "11:35", "12:10"]
                    # Ensure we have enough rows for all AM time slots
                    while len(blank_df) < len(am_times):
                        # Add a new row with the same structure as existing rows
                        new_row = pd.Series([''] * len(blank_df.columns), index=blank_df.columns)
                        blank_df = pd.concat([blank_df, pd.DataFrame([new_row])], ignore_index=True)
                    
                    # Update the time column in the dataframe
                    for i, time_slot in enumerate(am_times):
                        blank_df.iloc[i, 0] = time_slot
                    time_slots = am_times
                else:  # PM mode
                    pm_times = ["4:10", "4:45", "5:20", "5:55", "6:30", "7:05"]
                    # Ensure we have enough rows for all PM time slots
                    while len(blank_df) < len(pm_times):
                        # Add a new row with the same structure as existing rows
                        new_row = pd.Series([''] * len(blank_df.columns), index=blank_df.columns)
                        blank_df = pd.concat([blank_df, pd.DataFrame([new_row])], ignore_index=True)
                    
                    # Update the time column in the dataframe
                    for i, time_slot in enumerate(pm_times):
                        blank_df.iloc[i, 0] = time_slot
                    time_slots = pm_times
                
                class_columns = blank_df.columns[1:]

                # Reset manual selection when mode changes
                if 'manual_selection' not in st.session_state or 'current_mode' not in st.session_state or st.session_state.get('current_mode') != session_mode:
                    st.session_state.manual_selection = {
                        time_slot: {cls: False for cls in class_columns} for time_slot in time_slots
                    }
                    st.session_state['current_mode'] = session_mode

                # Create interactive grid
                for time_slot in time_slots:
                    st.markdown(f"#### {time_slot}")
                    cols = st.columns(len(class_columns))
                    for i, cls in enumerate(class_columns):
                        current_val = st.session_state.manual_selection[time_slot][cls]
                        new_val = cols[i].checkbox(cls, value=current_val, key=f"{time_slot}_{cls}")
                        st.session_state.manual_selection[time_slot][cls] = new_val
                
                # Show template generation button
                if st.button("Generate Template", type="primary"):
                    selected_matrix = pd.DataFrame.from_dict(st.session_state.manual_selection, orient='index')
                    selected_matrix.index.name = "Time"
                    selected_matrix.reset_index(inplace=True)

                    # Create final template with selected classes
                    final_template = blank_df.copy()
                    
                    # First, clear all class columns (except the time column)
                    for i in range(len(final_template)):
                        for j, cls in enumerate(class_columns):
                            final_template.loc[i, cls] = ""  # Clear all existing data
                    
                    # Then, only mark selected classes as "SELECTED"
                    for i, time_slot in enumerate(final_template.iloc[:, 0]):
                        if i < len(selected_matrix):
                            for j, cls in enumerate(class_columns):
                                if selected_matrix.loc[i, cls] == True:
                                    final_template.loc[i, cls] = "SELECTED"  # Marker for selected classes
                    
                    # Save the template directly to the assets folder
                    final_template.to_excel(blank_template_path, index=False, engine='openpyxl')

                    st.session_state['am_template_df'] = final_template
                    st.session_state['am_template_file'] = blank_template_path
                    st.session_state['manual_mode'] = True
                    st.session_state['template_generated'] = True

                    create_success_message("Template generated successfully!")
                    st.dataframe(final_template, height=400)

                    # Show continue button only if template was generated
                    if st.session_state.get('template_generated', False):
                        if st.button("Continue to Step 2", type="primary"):
                            # Clear the template_generated flag to prevent issues
                            st.session_state['template_generated'] = False
                            st.session_state.current_step = 2
                            st.rerun()
            else:
                st.error("Blank template file not found. Please ensure the template file exists in the assets folder.")
    
    # Step 2: Instructor Management
    elif current_step == 2:
        st.markdown("### 👥 Step 2: Add Instructors")
        
        # Show contextual help
        help_tip = ai_assistant.get_help_tip("instructor_entry")
        st.info(help_tip)
        
        # Get session mode from previous step
        session_mode = st.session_state.get('session_mode', 'AM')
        
        # Set default times based on session mode
        if session_mode == "AM":
            # AM session: 8:35-12:10, so default times are 8:05-12:40 (30 min before/after)
            default_start_time = time(8, 5)  # 8:05 AM
            default_end_time = time(12, 40)   # 12:40 PM
        else:  # PM mode
            # PM session: 4:10-7:05, so default times are 3:40-7:35 (30 min before/after)
            default_start_time = time(3, 40)   # 3:40 PM
            default_end_time = time(7, 35)     # 7:35 PM
        
        num_instructors = st.number_input(
            "Number of Instructors",
            min_value=1,
            max_value=20,
            value=3,
            help="How many instructors do you want to add?"
        )

        instructor_data = []
        
        for i in range(num_instructors):
            st.markdown(f"### Instructor {i+1}")
            
            # Get available instructor names from Firebase
            from firebase_config import firebase_manager
            firebase_instructors = firebase_manager.get_instructors(st.session_state.get('user_id'))
            available_instructors = [instructor_info.get('name', 'Unknown') for instructor_info in firebase_instructors.values()]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Instructor selection with manual typing capability
                
                # Show dropdown for quick selection
                st.markdown("**Quick Select from Saved Profiles:**")
                selected_profile = st.selectbox(
                    f"Select from profiles (optional)", 
                    ["None"] + available_instructors,
                    key=f"profile_{i}",
                    help="Choose from saved profiles or type manually below"
                )
                
                # Manual name input (always available)
                st.markdown("**Enter Instructor Name:**")
                if selected_profile == "None":
                    name = st.text_input(f"Name", key=f"name_{i}", placeholder="Enter instructor name")
                else:
                    # Pre-fill with selected profile but allow editing
                    name = st.text_input(f"Name", value=selected_profile, key=f"name_{i}", 
                                       placeholder="Enter instructor name or edit selected name")
                
                start_time = st.time_input(
                    f"{session_mode} Start Time", 
                    key=f"start_{i}",
                    value=default_start_time,
                    help=f"Default: 30 minutes before {session_mode} session starts"
                )
            
            with col2:
                end_time = st.time_input(
                    f"{session_mode} End Time", 
                    key=f"end_{i}",
                    value=default_end_time,
                    help=f"Default: 30 minutes after {session_mode} session ends"
                )
                role = st.selectbox(f"Role", ["Instructor", "Shadow"], key=f"role_{i}")
            
            # Class preferences with checkboxes
            st.markdown("#### 🚫 Classes They Can't Teach")
            
            # Get instructor profile if selected
            instructor_profile = None
            if selected_profile != "None":
                for instructor_info in firebase_instructors.values():
                    if instructor_info.get('name') == selected_profile:
                        instructor_profile = instructor_info
                        break
            
            available_classes = [
                "Starters", "P1", "P2", "P3", "Y1", "Y2", "Y3", "PSL",
                "STRK4", "STRK5", "STRK6", "TN BCS AD BCS", "TN STRK AD STRK",
                "TN/AD BSCS", "TN/AD STRKS", "CNDTNG"
            ]
            cant_teach_classes = []
            
            # Create checkboxes in a grid layout
            st.markdown("Select all classes this instructor cannot teach:")
            
            # Use columns for layout instead of container parameter
            cols = st.columns(4)
            for j, class_name in enumerate(available_classes):
                col_idx = j % 4
                
                # Pre-check if this class is in instructor's profile
                is_checked = False
                if instructor_profile and class_name in instructor_profile.get('cant_teach', []):
                    is_checked = True
                
                with cols[col_idx]:
                    if st.checkbox(class_name, value=is_checked, key=f"cant_teach_{i}_{class_name}"):
                        cant_teach_classes.append(class_name)
            
            # Convert list to string for compatibility with existing code
            cant_teach_str = ", ".join(cant_teach_classes) if cant_teach_classes else ""

            instructor_data.append({
                "Name": name,
                "AM Start": start_time,
                "AM End": end_time,
                "Can't Teach": cant_teach_str,
                "Role": role
            })

        # Template analysis button
        if st.button("📊 Analyze Template Requirements", type="secondary"):
            if 'am_template_df' in st.session_state and st.session_state['am_template_df'] is not None:
                template_df = st.session_state['am_template_df']
                
                st.markdown("### 📊 Template Analysis Results")
                
                # Count classes
                class_columns = [col for col in template_df.columns if col not in ['Time', 'brk']]
                total_classes = 0
                time_slots = len(template_df)
                
                for col in class_columns:
                    for _, row in template_df.iterrows():
                        if pd.notna(row[col]) and str(row[col]).strip() != '':
                            total_classes += 1
                
                # Calculate recommendations
                recommended_instructors = max(3, total_classes // 3)  # At least 3, or 1 per 3 classes
                
                # Show analysis
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Classes", total_classes)
                with col2:
                    st.metric("Time Slots", time_slots)
                with col3:
                    st.metric("Recommended Instructors", recommended_instructors)
                
                # Show class breakdown
                st.markdown("#### 📊 Class Breakdown")
                class_counts = {}
                for col in class_columns:
                    count = 0
                    for _, row in template_df.iterrows():
                        if pd.notna(row[col]) and str(row[col]).strip() != '':
                            count += 1
                    if count > 0:
                        class_counts[col] = count
                
                if class_counts:
                    class_df = pd.DataFrame(list(class_counts.items()), columns=['Class Type', 'Count'])
                    st.dataframe(class_df, use_container_width=True)
                
                # Show availability recommendations
                st.markdown("#### ⏰ Recommended Availability")
                session_mode = st.session_state.get('session_mode', 'AM')
                if session_mode == "AM":
                    st.markdown("**AM Session (8:35-12:10)**")
                    st.markdown("""
                    - **Start Time**: 8:05 AM (30 min before session)
                    - **End Time**: 12:40 PM (30 min after session)
                    - **Total Hours**: 4.5 hours
                    """)
                else:
                    st.markdown("**PM Session (4:10-7:05)**")
                    st.markdown("""
                    - **Start Time**: 3:40 PM (30 min before session)
                    - **End Time**: 7:35 PM (30 min after session)
                    - **Total Hours**: 3.9 hours
                    """)
                
                # Show break analysis
                st.markdown("#### 🚫 Break Analysis")
                break_slots = 0
                for _, row in template_df.iterrows():
                    if 'brk' in template_df.columns and pd.notna(row['brk']) and str(row['brk']).strip() != '':
                        break_slots += 1
                
                if break_slots > 0:
                    st.warning(f"⚠️ {break_slots} break slots detected. Consider reducing breaks for better coverage.")
                else:
                    st.success("✅ No excessive breaks detected. Good coverage distribution.")
            else:
                st.warning("Please upload a template first to analyze.")
        
        if st.button("Continue to Step 3", type="primary"):
            availability_df = pd.DataFrame(instructor_data)
            st.session_state['availability_df'] = availability_df
            
            # Show preview
            st.markdown("### 📋 Instructor Preview")
            st.dataframe(availability_df, height=300)
            
            # Create availability chart
            create_availability_chart(availability_df)
            
            st.session_state.current_step = 3
            st.rerun()
        
        # Add reset button
        if st.button("🔄 Start Over", type="secondary"):
            st.session_state.current_step = 1
            st.rerun()
    
    # Step 3: Generate Schedule
    elif current_step == 3:
        st.markdown("### ⚡ Step 3: Generate Schedule")
        
        # Show contextual help
        help_tip = ai_assistant.get_help_tip("schedule_generation")
        st.info(help_tip)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate Schedule", type="primary", use_container_width=True):
                create_loading_animation()
                
                availability_df = st.session_state.get('availability_df')
                am_template_df = st.session_state.get('am_template_df')
                am_template_file = st.session_state.get('am_template_file')
                manual_mode = st.session_state.get('manual_mode', False)

                if am_template_df is None or am_template_file is None:
                    create_error_message("No template data available. Please go back to step 1.")
                    return
                
                try:
                    output_stream, output_preview = generate_am_schedule(
                        am_template_df,
                        availability_df,
                        am_template_file,
                        manual_mode
                    )

                    st.session_state['output_stream'] = output_stream
                    st.session_state['output_preview'] = output_preview
                    st.session_state.schedule_generated = True
                    
                    create_success_message("Schedule generated successfully!")
                    
                    # Show preview
                    st.markdown("### 📊 Schedule Preview")
                    st.dataframe(pd.DataFrame(output_preview), height=400)
                    
                    # Create visualizations
                    create_schedule_visualization(pd.DataFrame(output_preview))
                    create_timeline_chart(pd.DataFrame(output_preview))
                    
                except Exception as e:
                    create_error_message(f"Error generating schedule: {str(e)}")
        
        with col2:
            if st.button("🔄 Start Over", type="secondary", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        
        # Show continue button to step 4 if schedule was generated
        if st.session_state.get('schedule_generated', False):
            if st.button("Continue to Download", type="primary", use_container_width=True):
                st.session_state.current_step = 4
                st.rerun()
    
    # Step 4: Download & Post Schedule
    elif current_step == 4:
        st.markdown("### 📥 Step 4: Download & Post Schedule")
        
        # Show contextual help
        help_tip = ai_assistant.get_help_tip("download")
        st.info(help_tip)
        
        if st.session_state.schedule_generated:
            # Schedule posting options
            st.markdown("#### 📤 Post Schedule Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Post Generated Schedule**")
                if st.button("📤 Post App-Generated Schedule", type="primary", use_container_width=True):
                    if st.session_state.get('output_preview'):
                        schedule_data = {
                            "schedule_data": st.session_state['output_preview'],
                            "template_file": st.session_state.get('am_template_file', ''),
                            "session_mode": st.session_state.get('session_mode', 'AM'),
                            "instructors_used": len(st.session_state.get('availability_df', pd.DataFrame())),
                            "posted_by": st.session_state.get('user_data', {}).get('email', 'Unknown')
                        }
                        
                        from firebase_config import firebase_manager
                        result = firebase_manager.post_schedule(schedule_data, st.session_state.get('user_id'))
                        if result["success"]:
                            instructor_emails = result.get("instructor_emails", [])
                            if instructor_emails:
                                st.success(f"✅ Schedule posted successfully!")
                                st.info(f"📧 **Posted to instructors:** {', '.join(instructor_emails)}")
                            else:
                                st.success("✅ Schedule posted successfully!")
                                st.warning("⚠️ No instructor emails found. Instructors won't be able to view this schedule.")
                        else:
                            st.error(f"❌ Failed to post schedule: {result.get('error', 'Unknown error')}")
                    else:
                        st.error("❌ No schedule generated yet. Please generate a schedule first.")
            
            with col2:
                st.markdown("**Upload & Post External Schedule**")
                uploaded_schedule = st.file_uploader(
                    "Upload Excel Schedule",
                    type=["xlsx"],
                    help="Upload a schedule file to post for instructors"
                )
                if uploaded_schedule and st.button("📤 Post Uploaded Schedule", type="primary", use_container_width=True):
                    try:
                        # Read the uploaded schedule
                        schedule_df = pd.read_excel(uploaded_schedule, engine="openpyxl")
                        schedule_data = {
                            "schedule_data": schedule_df.to_dict('records'),
                            "template_file": "uploaded_schedule.xlsx",
                            "session_mode": "Unknown",
                            "instructors_used": 0,
                            "posted_by": st.session_state.get('user_data', {}).get('email', 'Unknown')
                        }
                        
                        from firebase_config import firebase_manager
                        result = firebase_manager.post_schedule(schedule_data, st.session_state.get('user_id'))
                        if result["success"]:
                            instructor_emails = result.get("instructor_emails", [])
                            if instructor_emails:
                                st.success("✅ Uploaded schedule posted successfully!")
                                st.info(f"📧 **Posted to instructors:** {', '.join(instructor_emails)}")
                            else:
                                st.success("✅ Uploaded schedule posted successfully!")
                                st.warning("⚠️ No instructor emails found. Instructors won't be able to view this schedule.")
                            # Clear the uploaded file to show the success message
                            st.session_state.uploaded_schedule = None
                        else:
                            st.error(f"❌ Failed to post schedule: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"❌ Error processing uploaded file: {str(e)}")
            
            st.markdown("---")
            
            # Download options
            st.markdown("#### 📥 Download Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📅 Download Excel Schedule",
                    data=st.session_state.get('output_stream'),
                    file_name=f"AM_Schedule_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col2:
                if st.button("🔄 Generate New Schedule", use_container_width=True):
                    st.session_state.current_step = 1
                    st.session_state.schedule_generated = False
                    st.rerun()
            
            # Add reset button
            if st.button("🔄 Start Over", type="secondary"):
                st.session_state.current_step = 1
                st.session_state.schedule_generated = False
                st.rerun()
            
            # Show schedule preview
            st.markdown("### 📊 Schedule Preview")
            if st.session_state.get('output_preview'):
                preview_df = pd.DataFrame(st.session_state['output_preview'])
                st.dataframe(preview_df, height=400)
            
            st.markdown("### 📊 Schedule Analytics")
            create_progress_dashboard(
                st.session_state.get('availability_df'),
                st.session_state.get('am_template_df')
            )

def show_instructor_management():
    """Show instructor management interface"""
    st.markdown("## 👥 Instructor Management")
    
    # Session mode selection
    session_mode = st.radio(
        "Session Mode",
        ["AM", "PM"],
        horizontal=True,
        help="AM: 8:35-12:10, PM: 4:10-7:05"
    )
    
    # Set default times based on session mode
    if session_mode == "AM":
        default_start_time = time(8, 5)  # 8:05 AM
        default_end_time = time(12, 40)   # 12:40 PM
    else:  # PM mode
        default_start_time = time(3, 40)   # 3:40 PM
        default_end_time = time(7, 35)     # 7:35 PM
    
    # Tab for managing instructor profiles and template analysis
    tab1, tab2, tab3 = st.tabs(["📋 Manage Profiles", "➕ Add New Instructor", "📊 Template Analysis"])
    
    with tab1:
        st.markdown("### 📋 Current Instructor Profiles")
        
        # Get Firebase instructors
        from firebase_config import firebase_manager
        firebase_instructors = firebase_manager.get_instructors(st.session_state.get('user_id'))
        
        # Display Firebase instructors
        all_instructors = []
        
        # Add Firebase instructors
        for instructor_id, instructor_data in firebase_instructors.items():
            all_instructors.append({
                'source': 'firebase',
                'id': instructor_id,
                'data': instructor_data
            })
        
        if not all_instructors:
            st.info("No instructor profiles found. Add your first instructor in the 'Add New Instructor' tab.")
        else:
            for i, instructor_info in enumerate(all_instructors):
                instructor = instructor_info['data']
                source = instructor_info['source']
                
                # Create display name
                display_name = f"👤 {instructor.get('name', 'Unknown')} - {instructor.get('role', 'Unknown')}"
                
                with st.expander(display_name, expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Name:** {instructor.get('name', 'N/A')}")
                        st.markdown(f"**Role:** {instructor.get('role', 'N/A')}")
                        if instructor.get('email'):
                            st.markdown(f"**Email:** {instructor['email']}")
                        st.markdown(f"**Can't Teach:** {', '.join(instructor.get('cant_teach', [])) if instructor.get('cant_teach') else 'None'}")
                        
                        if instructor.get('default_start_time') and instructor.get('default_end_time'):
                            st.markdown(f"**Default Times:** {instructor['default_start_time']} - {instructor['default_end_time']}")
                        
                        # Show schedule access info if instructor has email
                        if instructor.get('email'):
                            st.success(f"✅ This instructor can view schedules when they sign in with: {instructor['email']}")
                        else:
                            st.info("ℹ️ Add an email to enable schedule viewing for this instructor")
                    
                    with col2:
                        # Edit button
                        if st.button(f"✏️ Edit", key=f"edit_{i}", type="secondary"):
                            st.session_state.editing_instructor = instructor_info
                            st.rerun()
                        
                        # Delete button
                        if st.button(f"🗑️ Delete", key=f"delete_{i}", type="secondary"):
                            if firebase_manager.delete_instructor(instructor_info['id']):
                                st.success(f"Deleted {instructor.get('name')} from Firebase")
                                st.rerun()
                            else:
                                st.error("Failed to delete from Firebase")
        
        # Edit instructor form
        if 'editing_instructor' in st.session_state:
            st.markdown("---")
            st.markdown("### ✏️ Edit Instructor")
            
            instructor_info = st.session_state.editing_instructor
            instructor = instructor_info['data']
            
            col1, col2 = st.columns(2)
            
            with col1:
                edit_name = st.text_input("Name", value=instructor.get('name', ''), key="edit_name")
                edit_email = st.text_input("Email (Optional)", value=instructor.get('email', ''), key="edit_email")
                edit_role = st.selectbox("Role", ["Instructor", "Shadow"], index=0 if instructor.get('role') == "Instructor" else 1, key="edit_role")
            
            with col2:
                edit_start = st.time_input(
                    f"{session_mode} Start Time",
                    value=time.fromisoformat(instructor.get('default_start_time', '08:05:00')) if instructor.get('default_start_time') else default_start_time,
                    key="edit_start"
                )
                edit_end = st.time_input(
                    f"{session_mode} End Time",
                    value=time.fromisoformat(instructor.get('default_end_time', '12:40:00')) if instructor.get('default_end_time') else default_end_time,
                    key="edit_end"
                )
            
            # Class preferences
            st.markdown("### 🚫 Classes They Can't Teach")
            current_cant_teach = instructor.get('cant_teach', [])
            available_classes = [
                "Starters", "P1", "P2", "P3", "Y1", "Y2", "Y3", "PSL",
                "STRK4", "STRK5", "STRK6", "TN BCS AD BCS", "TN STRK AD STRK",
                "TN/AD BSCS", "TN/AD STRKS", "CNDTNG"
            ]
            edit_cant_teach_classes = []
            
            cols = st.columns(4)
            for j, class_name in enumerate(available_classes):
                col_idx = j % 4
                with cols[col_idx]:
                    is_checked = class_name in current_cant_teach
                    if st.checkbox(class_name, value=is_checked, key=f"edit_cant_teach_{class_name}"):
                        edit_cant_teach_classes.append(class_name)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Changes", type="primary"):
                    updated_data = {
                        "name": edit_name,
                        "email": edit_email,
                        "role": edit_role,
                        "cant_teach": edit_cant_teach_classes,
                        "default_start_time": str(edit_start),
                        "default_end_time": str(edit_end)
                    }
                    
                    if firebase_manager.update_instructor(instructor_info['id'], updated_data):
                        st.success("Instructor updated successfully!")
                        del st.session_state.editing_instructor
                        st.rerun()
                    else:
                        st.error("Failed to update instructor")
            
            with col2:
                if st.button("❌ Cancel", type="secondary"):
                    del st.session_state.editing_instructor
                    st.rerun()
    
    with tab2:
        st.markdown("### ➕ Add New Instructor Profile")
        
        # Instructor details
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Name", placeholder="Enter instructor name")
            new_email = st.text_input("Email (Optional)", placeholder="Enter instructor email")
            new_role = st.selectbox("Role", ["Instructor", "Shadow"])
        
        with col2:
            new_start = st.time_input(
                f"{session_mode} Start Time",
                value=default_start_time,
                help=f"Default: 30 minutes before {session_mode} session starts"
            )
            new_end = st.time_input(
                f"{session_mode} End Time",
                value=default_end_time,
                help=f"Default: 30 minutes after {session_mode} session ends"
            )
        
        # Class preferences with checkboxes
        st.markdown("### 🚫 Classes They Can't Teach")
        st.markdown("Select all classes this instructor cannot teach:")
        
        available_classes = [
            "Starters", "P1", "P2", "P3", "Y1", "Y2", "Y3", "PSL",
            "STRK4", "STRK5", "STRK6", "TN BCS AD BCS", "TN STRK AD STRK",
            "TN/AD BSCS", "TN/AD STRKS", "CNDTNG"
        ]
        cant_teach_classes = []
        
        # Create checkboxes in columns for better layout
        cols = st.columns(4)
        for i, class_name in enumerate(available_classes):
            col_idx = i % 4
            with cols[col_idx]:
                if st.checkbox(class_name, key=f"cant_teach_{class_name}"):
                    cant_teach_classes.append(class_name)
        
        if st.button("Add Instructor Profile", type="primary"):
            if new_name.strip():
                # Add to Firebase
                new_instructor_data = {
                    "name": new_name.strip(),
                    "email": new_email.strip() if new_email.strip() else None,
                    "role": new_role,
                    "cant_teach": cant_teach_classes,
                    "default_start_time": str(new_start),
                    "default_end_time": str(new_end)
                }
                from firebase_config import firebase_manager
                if firebase_manager.add_instructor(new_instructor_data, st.session_state.get('user_id')):
                    st.success(f"Instructor '{new_name}' added successfully!")
                    # Clear form
                    st.rerun()
                else:
                    st.error("❌ Failed to add instructor")
            else:
                st.error("Please enter a name for the instructor.")
    
    with tab3:
        st.markdown("### 📊 Template Analysis")
        st.markdown("Upload a template to analyze instructor requirements and recommendations.")
        
        uploaded_template = st.file_uploader(
            "Upload Template for Analysis",
            type=["xlsx"],
            help="Upload a schedule template to analyze instructor needs"
        )
        
        if uploaded_template:
            try:
                # Read the template
                template_df = pd.read_excel(uploaded_template, engine="openpyxl")
                
                # Analyze the template
                st.markdown("#### 📋 Template Analysis Results")
                
                # Count classes
                class_columns = [col for col in template_df.columns if col not in ['Time', 'brk']]
                total_classes = 0
                time_slots = len(template_df)
                
                for col in class_columns:
                    for _, row in template_df.iterrows():
                        if pd.notna(row[col]) and str(row[col]).strip() != '':
                            total_classes += 1
                
                # Calculate recommendations
                recommended_instructors = max(3, total_classes // 3)  # At least 3, or 1 per 3 classes
                
                # Show analysis
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Classes", total_classes)
                with col2:
                    st.metric("Time Slots", time_slots)
                with col3:
                    st.metric("Recommended Instructors", recommended_instructors)
                
                # Show class breakdown
                st.markdown("#### 📊 Class Breakdown")
                class_counts = {}
                for col in class_columns:
                    count = 0
                    for _, row in template_df.iterrows():
                        if pd.notna(row[col]) and str(row[col]).strip() != '':
                            count += 1
                    if count > 0:
                        class_counts[col] = count
                
                if class_counts:
                    class_df = pd.DataFrame(list(class_counts.items()), columns=['Class Type', 'Count'])
                    st.dataframe(class_df, use_container_width=True)
                
                # Show availability recommendations
                st.markdown("#### ⏰ Recommended Availability")
                if session_mode == "AM":
                    st.markdown("**AM Session (8:35-12:10)**")
                    st.markdown("""
                    - **Start Time**: 8:05 AM (30 min before session)
                    - **End Time**: 12:40 PM (30 min after session)
                    - **Total Hours**: 4.5 hours
                    """)
                else:
                    st.markdown("**PM Session (4:10-7:05)**")
                    st.markdown("""
                    - **Start Time**: 3:40 PM (30 min before session)
                    - **End Time**: 7:35 PM (30 min after session)
                    - **Total Hours**: 3.9 hours
                    """)
                
                # Show break analysis
                st.markdown("#### 🚫 Break Analysis")
                break_slots = 0
                for _, row in template_df.iterrows():
                    if 'brk' in template_df.columns and pd.notna(row['brk']) and str(row['brk']).strip() != '':
                        break_slots += 1
                
                if break_slots > 0:
                    st.warning(f"⚠️ {break_slots} break slots detected. Consider reducing breaks for better coverage.")
                else:
                    st.success("✅ No excessive breaks detected. Good coverage distribution.")
                
            except Exception as e:
                st.error(f"Error analyzing template: {str(e)}")

def show_ai_assistant():
    """Show the AI assistant chatbot"""
    st.markdown("## 🤖 AI Assistant")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # API Key status
    st.markdown("### 🔑 API Status")
    if ai_assistant.client:
        st.success("✅ AI Assistant Ready!")
    else:
        st.error("❌ AI Assistant not configured. Please update the API key in ai_assistant.py")
    
    # Custom GPT Button
    st.markdown("### 🚀 Try Our Custom GPT")
    st.markdown(ai_assistant.get_custom_gpt_button(), unsafe_allow_html=True)
    
    # Chat interface
    st.markdown("### 💬 Chat with AI Assistant")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 1rem; border-radius: 1rem; margin: 0.5rem 0; 
                                color: white; text-align: right;">
                        <strong>You:</strong><br>
                        {message['content']}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                padding: 1rem; border-radius: 1rem; margin: 0.5rem 0; 
                                color: white;">
                        <strong>AI Assistant:</strong><br>
                        {message['content']}
                    </div>
                """, unsafe_allow_html=True)
    
    # Input area
    user_input = st.text_area(
        "Ask me anything about the swim scheduling app!",
        placeholder="e.g., How do I create a schedule? What's the difference between AM and PM modes?",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Send", type="primary"):
            if user_input.strip():
                # Add user message to history
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input
                })
                
                # Get AI response
                ai_response = ai_assistant.chat_with_ai(user_input, st.session_state.chat_history)
                
                # Add AI response to history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': ai_response
                })
                
                st.rerun()
    
    with col2:
        if st.button("Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Quick help topics
    st.markdown("### 🚀 Quick Help Topics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 How to use Template Mode"):
            st.session_state.chat_history.append({
                'role': 'user',
                'content': "How do I use Template Mode?"
            })
            ai_response = ai_assistant.chat_with_ai("How do I use Template Mode?", st.session_state.chat_history)
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': ai_response
            })
            st.rerun()
    
    with col2:
        if st.button("🎯 How to use Manual Mode"):
            st.session_state.chat_history.append({
                'role': 'user',
                'content': "How do I use Manual Mode?"
            })
            ai_response = ai_assistant.chat_with_ai("How do I use Manual Mode?", st.session_state.chat_history)
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': ai_response
            })
            st.rerun()
    
    with col3:
        if st.button("👥 Manage Instructors"):
            st.session_state.chat_history.append({
                'role': 'user',
                'content': "How do I manage instructor profiles?"
            })
            ai_response = ai_assistant.chat_with_ai("How do I manage instructor profiles?", st.session_state.chat_history)
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': ai_response
            })
            st.rerun()
    
    # Schedule analysis
    if 'schedule_generated' in st.session_state and st.session_state.schedule_generated:
        st.markdown("### 📊 Schedule Analysis")
        
        if st.button("Analyze Current Schedule"):
            # Get current schedule data (you'll need to implement this based on your data structure)
            schedule_data = {
                "message": "Schedule analysis feature coming soon!",
                "timestamp": datetime.now().isoformat()
            }
            
            analysis = ai_assistant.analyze_schedule(schedule_data)
            st.markdown(f"**Analysis:**\n{analysis}")

def show_analytics():
    """Show analytics and insights"""
    st.markdown("## 📊 Analytics & Insights")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("Total Classes", "156", "+12", "normal")
    
    with col2:
        create_metric_card("Instructor Hours", "1,248", "+89", "normal")
    
    with col3:
        create_metric_card("Coverage Rate", "94.2%", "+2.1%", "normal")
    
    with col4:
        create_metric_card("Efficiency Score", "87.5%", "+5.2%", "normal")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Weekly Coverage Trend")
        # Mock chart data
        chart_data = pd.DataFrame({
            'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'Coverage': [85, 88, 92, 94]
        })
        st.line_chart(chart_data.set_index('Week'))
    
    with col2:
        st.markdown("### 👥 Instructor Utilization")
        # Mock pie chart data
        utilization_data = pd.DataFrame({
            'Instructor': ['Sarah', 'Mike', 'Emma', 'Alex'],
            'Hours': [25, 22, 18, 20]
        })
        st.bar_chart(utilization_data.set_index('Instructor'))

def show_settings():
    """Show settings and configuration"""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### 🔐 Authentication")
    st.text_input("Admin Username", value="admin", disabled=True)
    st.text_input("Admin Password", value="••••••••", type="password")
    
    st.markdown("### 🎨 Appearance")
    theme = st.selectbox("Theme", ["Dark", "Light", "Auto"])
    accent_color = st.color_picker("Accent Color", value="#00d4ff")
    
    st.markdown("### 📧 Notifications")
    email_notifications = st.checkbox("Enable Email Notifications", value=True)
    schedule_reminders = st.checkbox("Schedule Reminders", value=True)
    
    if st.button("Save Settings", type="primary"):
        create_success_message("Settings saved successfully!")

def show_help():
    """Show help and documentation"""
    st.markdown("## ❓ Help & Documentation")
    
    st.markdown("### 🚀 Getting Started")
    
    with st.expander("How to create a schedule", expanded=True):
        st.markdown("""
        1. **Upload Template**: Start by uploading your Excel template or manually selecting classes
        2. **Add Instructors**: Enter instructor details including availability and preferences
        3. **Generate Schedule**: Let the AI create an optimized schedule
        4. **Download**: Get your final schedule in Excel format
        """)
    
    with st.expander("Understanding the Interface"):
        st.markdown("""
        - **Dashboard**: Overview of your scheduling system
        - **Schedule Generator**: Create new schedules step by step
        - **Instructor Management**: Add and manage instructor profiles
        - **Analytics**: View performance metrics and insights
        """)
    
    with st.expander("Troubleshooting"):
        st.markdown("""
        **Common Issues:**
        - Template not uploading: Ensure file is in .xlsx format
        - Schedule generation fails: Check instructor availability
        - Download issues: Clear browser cache and try again
        """)

def show_employee_schedule_view():
    """Show employee schedule view with posted schedule"""
    st.markdown("## 📋 Current Schedule")
    
    # Get active schedule from Firebase (filtered by user email)
    from firebase_config import firebase_manager
    user_email = st.session_state.get('user_data', {}).get('email', '')
    active_schedule = firebase_manager.get_active_schedule(user_email)
    
    if active_schedule:
        st.success("✅ Active schedule found!")
        
        # Show schedule info
        schedule_info = active_schedule
        st.markdown(f"**Posted by:** {schedule_info.get('posted_by', 'Unknown')}")
        st.markdown(f"**Session Mode:** {schedule_info.get('session_mode', 'Unknown')}")
        st.markdown(f"**Instructors Used:** {schedule_info.get('instructors_used', 0)}")
        
        # Convert schedule data to DataFrame
        if 'schedule_data' in schedule_info:
            schedule_df = pd.DataFrame(schedule_info['schedule_data'])
            st.dataframe(schedule_df, use_container_width=True)
            
            # Show employee-specific assignments
            employee_email = st.session_state.get('user_data', {}).get('email', '')
            
            st.markdown("---")
            st.markdown(f"### 👤 Your Assignments ({employee_email})")
            
            # Filter assignments for this employee
            employee_assignments = []
            for _, row in schedule_df.iterrows():
                for col in schedule_df.columns:
                    if col != 'Time' and col != 'brk' and pd.notna(row[col]) and str(row[col]).strip() != '':
                        # Simple matching - in real app, you'd match by email
                        if employee_email and employee_email.lower() in str(row[col]).lower():
                            employee_assignments.append({
                                'Time': row['Time'],
                                'Class': col,
                                'Assignment': row[col]
                            })
            
            if employee_assignments:
                st.markdown("#### 📅 Your Schedule Today")
                for assignment in employee_assignments:
                    st.markdown(f"**{assignment['Time']}**: {assignment['Class']} - {assignment['Assignment']}")
                
                # Show metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Today's Classes", len(employee_assignments))
                with col2:
                    st.metric("Total Students", "23")
                with col3:
                    st.metric("Break Time", "2 hours")
            else:
                st.info("No specific assignments found for your email. This may be a demo schedule.")
        else:
            st.error("Schedule data not found in the posted schedule.")
    else:
        st.info("📋 No active schedule posted yet. Check back later or contact your supervisor.")
        
        # Show demo schedule for reference
        st.markdown("#### Demo Schedule (for reference)")
        demo_schedule = pd.DataFrame({
            'Time': ['8:35', '9:10', '9:45', '10:20', '11:00', '11:35', '12:10'],
            'Starters': ['', '', '', '', '', '', ''],
            'P1': ['Sarah', 'Mike', '', 'Emma', '', 'Alex', ''],
            'P2': ['', 'Sarah', 'Mike', '', 'Emma', '', 'Alex'],
            'P3': ['Mike', '', 'Sarah', 'Mike', 'Sarah', 'Mike', ''],
            'Y1': ['Emma', 'Alex', 'Emma', '', 'Mike', 'Sarah', ''],
            'Y2': ['Alex', 'Emma', 'Alex', 'Emma', 'Alex', '', 'Mike'],
            'Y3': ['', 'Mike', 'Sarah', 'Alex', 'Emma', 'Alex', 'Sarah'],
            'PSL': ['Private 1', 'Private 2', '', 'Private 3', '', 'Private 4', ''],
            'STRK4': ['', 'Sarah', 'Mike', '', 'Emma', 'Alex', ''],
            'STRK5': ['Mike', '', 'Sarah', 'Mike', '', 'Sarah', ''],
            'STRK6': ['Sarah', 'Mike', '', 'Emma', 'Alex', '', 'Mike'],
            'TN/AD BSCS': ['', 'Emma', 'Alex', '', 'Sarah', 'Mike', ''],
            'TN/AD STRKS': ['Alex', '', 'Emma', 'Alex', '', 'Emma', ''],
            'CNDTNG': ['Emma', 'Alex', '', 'Mike', 'Sarah', '', 'Alex'],
            'brk': ['Break', 'Break', 'Break', 'Break', 'Break', 'Break', 'Break']
        })
        
        st.dataframe(demo_schedule, use_container_width=True)

def show_employee_dashboard():
    """Show employee dashboard with posted schedule view"""
    st.markdown("## 👋 Welcome, Employee!")
    
    # Show posted schedule if available
    st.markdown("### 📋 Current Schedule")
    
    # Get active schedule from Firebase (filtered by user email)
    from firebase_config import firebase_manager
    user_email = st.session_state.get('user_data', {}).get('email', '')
    active_schedule = firebase_manager.get_active_schedule(user_email)
    
    if active_schedule:
        st.success("✅ Active schedule found!")
        
        # Show schedule info
        schedule_info = active_schedule
        st.markdown(f"**Posted by:** {schedule_info.get('posted_by', 'Unknown')}")
        st.markdown(f"**Session Mode:** {schedule_info.get('session_mode', 'Unknown')}")
        st.markdown(f"**Instructors Used:** {schedule_info.get('instructors_used', 0)}")
        
        # Convert schedule data to DataFrame
        if 'schedule_data' in schedule_info:
            schedule_df = pd.DataFrame(schedule_info['schedule_data'])
            st.dataframe(schedule_df, use_container_width=True)
            
            # Show employee-specific assignments
            employee_email = st.session_state.get('user_data', {}).get('email', '')
            
            st.markdown("---")
            st.markdown(f"### 👤 Your Assignments ({employee_email})")
            
            # Filter assignments for this employee
            employee_assignments = []
            for _, row in schedule_df.iterrows():
                for col in schedule_df.columns:
                    if col != 'Time' and col != 'brk' and pd.notna(row[col]) and str(row[col]).strip() != '':
                        # Simple matching - in real app, you'd match by email
                        if employee_email and employee_email.lower() in str(row[col]).lower():
                            employee_assignments.append({
                                'Time': row['Time'],
                                'Class': col,
                                'Assignment': row[col]
                            })
            
            if employee_assignments:
                st.markdown("#### 📅 Your Schedule Today")
                for assignment in employee_assignments:
                    st.markdown(f"**{assignment['Time']}**: {assignment['Class']} - {assignment['Assignment']}")
                
                # Show metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Today's Classes", len(employee_assignments))
                with col2:
                    st.metric("Total Students", "23")
                with col3:
                    st.metric("Break Time", "2 hours")
            else:
                st.info("No specific assignments found for your email. This may be a demo schedule.")
        else:
            st.error("Schedule data not found in the posted schedule.")
    else:
        st.info("📋 No active schedule posted yet. Check back later or contact your supervisor.")
        
        # Show demo schedule for reference
        st.markdown("#### Demo Schedule (for reference)")
        demo_schedule = pd.DataFrame({
            'Time': ['8:35', '9:10', '9:45', '10:20', '11:00', '11:35', '12:10'],
            'Starters': ['', '', '', '', '', '', ''],
            'P1': ['Sarah', 'Mike', '', 'Emma', '', 'Alex', ''],
            'P2': ['', 'Sarah', 'Mike', '', 'Emma', '', 'Alex'],
            'P3': ['Mike', '', 'Sarah', 'Mike', 'Sarah', 'Mike', ''],
            'Y1': ['Emma', 'Alex', 'Emma', '', 'Mike', 'Sarah', ''],
            'Y2': ['Alex', 'Emma', 'Alex', 'Emma', 'Alex', '', 'Mike'],
            'Y3': ['', 'Mike', 'Sarah', 'Alex', 'Emma', 'Alex', 'Sarah'],
            'PSL': ['Private 1', 'Private 2', '', 'Private 3', '', 'Private 4', ''],
            'STRK4': ['', 'Sarah', 'Mike', '', 'Emma', 'Alex', ''],
            'STRK5': ['Mike', '', 'Sarah', 'Mike', '', 'Sarah', ''],
            'STRK6': ['Sarah', 'Mike', '', 'Emma', 'Alex', '', 'Mike'],
            'TN/AD BSCS': ['', 'Emma', 'Alex', '', 'Sarah', 'Mike', ''],
            'TN/AD STRKS': ['Alex', '', 'Emma', 'Alex', '', 'Emma', ''],
            'CNDTNG': ['Emma', 'Alex', '', 'Mike', 'Sarah', '', 'Alex'],
            'brk': ['Break', 'Break', 'Break', 'Break', 'Break', 'Break', 'Break']
        })
        
        st.dataframe(demo_schedule, use_container_width=True)

# Run the main application
if __name__ == "__main__":
    main()