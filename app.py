# app.py - Futuristic Swim Scheduler

import streamlit as st
from auth import login_form
from scheduler import generate_am_schedule
from template_parser import parse_template
from ui_components import *
from instructor_manager import instructor_manager
import pandas as pd
import io
import tempfile
from datetime import datetime, time
import os
from openpyxl import load_workbook, Workbook, styles
from shutil import copyfile
from ai_assistant import ai_assistant
from enrollment_parser import EnrollmentParser

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

# --- Login Section --- #
if not st.session_state.logged_in:
    login_form()
    st.stop()

# --- Main Application --- #
def main():
    # Create header
    create_header()
    
    # Create sidebar navigation
    current_section = create_sidebar_menu()
    
    # Main content based on navigation
    if current_section == "dashboard":
        show_dashboard()
    elif current_section == "schedule":
        show_schedule_generator()
    elif current_section == "instructors":
        show_instructor_management()
    elif current_section == "ai_assistant":
        show_ai_assistant()
    elif current_section == "analytics":
        show_analytics()
    elif current_section == "settings":
        show_settings()
    elif current_section == "help":
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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📅 Generate New Schedule", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        if st.button("👥 Manage Instructors", use_container_width=True):
            st.session_state.current_section = "instructors"
            st.rerun()
    
    with col3:
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
            
            # Date selection
            schedule_date = st.date_input(
                "Select Schedule Date",
                value=datetime.now().date(),
                help="Choose the date for which you want to generate the schedule"
            )
            
            # Session mode selection
            session_mode = st.radio(
                "Session Mode",
                ["AM", "PM"],
                horizontal=True,
                help="AM: 8:35-12:10, PM: 4:10-7:05"
            )
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
                if st.button("🚀 Generate Schedule from Enrollments", type="primary"):
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
                                preview_df = parser.get_template_preview(group_classes, private_lessons, session_mode)
                                st.session_state['am_template_df'] = preview_df
                                
                                # Set template generated flag for enrollment mode
                                st.session_state['template_generated'] = True
                                st.session_state['enrollment_mode'] = True
                                st.session_state['am_template_file'] = "assets/Blank_MTWT_Template1.xlsx"
                                
                                create_success_message(f"Schedule template generated successfully for {schedule_date.strftime('%A, %B %d, %Y')}!")
                                
                                # Show preview
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
            
            # Get available instructor names for dropdown
            available_instructors = instructor_manager.get_instructor_names()
            available_instructors.insert(0, "Select from profiles...")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Instructor selection with manual typing capability
                available_instructors = instructor_manager.get_instructor_names()
                
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
                instructor_profile = instructor_manager.get_instructor_by_name(selected_profile)
            
            available_classes = instructor_manager.get_available_classes()
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
    
    # Step 4: Download
    elif current_step == 4:
        st.markdown("### 📥 Step 4: Download Schedule")
        
        # Show contextual help
        help_tip = ai_assistant.get_help_tip("download")
        st.info(help_tip)
        
        if st.session_state.schedule_generated:
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
    
    # Tab for managing instructor profiles
    tab1, tab2 = st.tabs(["📋 Manage Profiles", "➕ Add New Instructor"])
    
    with tab1:
        st.markdown("### 📋 Current Instructor Profiles")
        
        instructors = instructor_manager.get_all_instructors()
        
        if not instructors:
            st.info("No instructor profiles found. Add your first instructor in the 'Add New Instructor' tab.")
        else:
            for i, instructor in enumerate(instructors):
                with st.expander(f"👤 {instructor['name']} - {instructor['role']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Name:** {instructor['name']}")
                        st.markdown(f"**Role:** {instructor['role']}")
                        st.markdown(f"**Can't Teach:** {', '.join(instructor['cant_teach']) if instructor['cant_teach'] else 'None'}")
                        
                        if instructor['default_start_time'] and instructor['default_end_time']:
                            st.markdown(f"**Default Times:** {instructor['default_start_time']} - {instructor['default_end_time']}")
                    
                    with col2:
                        if st.button(f"🗑️ Delete", key=f"delete_{i}", type="secondary"):
                            if instructor_manager.delete_instructor(instructor['name']):
                                st.success(f"Deleted {instructor['name']}")
                                st.rerun()
                            else:
                                st.error("Failed to delete instructor")
    
    with tab2:
        st.markdown("### ➕ Add New Instructor Profile")
        
        # Instructor details
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Name", placeholder="Enter instructor name")
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
        
        available_classes = instructor_manager.get_available_classes()
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
                if instructor_manager.add_instructor(
                    name=new_name.strip(),
                    role=new_role,
                    cant_teach=cant_teach_classes,
                    default_start_time=new_start,
                    default_end_time=new_end
                ):
                    st.success(f"Instructor '{new_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("An instructor with this name already exists!")
            else:
                st.error("Please enter a name for the instructor.")

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

# Run the main application
if __name__ == "__main__":
    main()