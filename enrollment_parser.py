# enrollment_parser.py - Parse enrollment Excel files to generate schedule templates

import pandas as pd
from datetime import datetime, timedelta
from openpyxl import load_workbook
import os

class EnrollmentParser:
    def __init__(self):
        self.class_mapping = {
            # Starters
            "Swim Starters Stage A Exploration": "Starters",
            "Swim Starters Stage B Exploration": "Starters",
            
            # Preschool
            "Preschool Stage 1 Water Acclimation": "P1",
            "Preschool Stage 2 Water Movement": "P2", 
            "Preschool Stage 3 Water Stamina": "P3",
            
            # School Age
            "School Age Stage 1 Water Acclimation": "Y1",
            "School Age Stage 2 Water Movement": "Y2",
            "School Age Stage 3 Water Stamina": "Y3",
            
            # Stroke Development
            "School Age Stage 4 Stroke Introduction": "STRK4",
            "School Age Stage 5 Stroke Development": "STRK5", 
            "School Age Stage 6 Stroke Mechanics": "STRK6",
            
            # Teen/Adult
            "Teen / Adult Swim Basics": "TN/AD BSCS",
            "Teen / Adult Swim Strokes": "TN/AD STRKS",
            
            # Conditioning
            "Aquatic Conditioning Swim Team Prep": "CNDTNG"
        }
        
        # Time slot mapping for AM/PM
        self.am_times = ["8:35", "9:10", "9:45", "10:20", "11:00", "11:35", "12:10"]
        self.pm_times = ["4:10", "4:45", "5:20", "5:55", "6:30", "7:05"]
    
    def parse_group_lessons(self, file_path, target_date, session_mode):
        """Parse group lessons Excel file and extract classes for the target date"""
        try:
            df = pd.read_excel(file_path)
            
            # Convert target_date to datetime if it's a string
            if isinstance(target_date, str):
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            elif isinstance(target_date, datetime):
                target_date = target_date.date()
            
            # Get day of week for target date
            target_day = target_date.strftime('%A')
            
            # Filter for the target date and session mode
            classes = []
            
            for _, row in df.iterrows():
                # Check if this row is for the target day
                day_of_week = str(row.get('Day of Week', '')).strip()
                if not day_of_week or target_day not in day_of_week:
                    continue
                
                # Get course name and map to class type
                course_name = str(row.get('Course Option: Course Option Name', '')).strip()
                if course_name not in self.class_mapping:
                    continue
                
                class_type = self.class_mapping[course_name]
                
                # Get start time and check if it's in the correct session
                start_time_str = str(row.get('Course Start Time', '')).strip()
                if not start_time_str or start_time_str == 'nan':
                    continue
                
                # Parse time and check session
                try:
                    if ':' in start_time_str:
                        # Handle different time formats (e.g., "8:00 AM", "8:00", "20:00")
                        time_parts = start_time_str.split(':')
                        hour_str = time_parts[0].strip()
                        minute_str = time_parts[1].split()[0].strip() if ' ' in time_parts[1] else time_parts[1].strip()
                        
                        hour = int(hour_str)
                        minute = int(minute_str)
                        
                        # Convert to 24-hour format if needed
                        if 'PM' in start_time_str.upper() and hour != 12:
                            hour += 12
                        elif 'AM' in start_time_str.upper() and hour == 12:
                            hour = 0
                        
                        # Check if time is in the correct session
                        if session_mode == "AM":
                            # AM session: 8:00 AM - 12:45 PM
                            if 8 <= hour <= 12:
                                classes.append({
                                    'class_type': class_type,
                                    'start_time': f"{hour:02d}:{minute:02d}",
                                    'enrollment': int(row.get('Total Enrolled', 0))
                                })
                        elif session_mode == "PM":
                            # PM session: 3:45 PM - 8:00 PM
                            if hour >= 15 or hour < 8:
                                classes.append({
                                    'class_type': class_type,
                                    'start_time': f"{hour:02d}:{minute:02d}",
                                    'enrollment': int(row.get('Total Enrolled', 0))
                                })
                except (ValueError, IndexError):
                    continue
            
            return classes
            
        except Exception as e:
            print(f"Error parsing group lessons: {e}")
            return []
    
    def parse_private_lessons(self, file_path, target_date, session_mode):
        """Parse private lessons Excel file and extract classes for the target date"""
        try:
            df = pd.read_excel(file_path)
            
            # Convert target_date to datetime if it's a string
            if isinstance(target_date, str):
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            elif isinstance(target_date, datetime):
                target_date = target_date.date()
            
            private_lessons = []
            
            for _, row in df.iterrows():
                course_option = str(row.get('Course Option', '')).strip()
                start_date_str = str(row.get('Start Date', '')).strip()
                start_time_str = str(row.get('Start Time', '')).strip()
                
                if not start_date_str or start_date_str == 'nan':
                    continue
                
                try:
                    # Parse start date
                    start_date = pd.to_datetime(start_date_str).date()
                    
                    # Check if this lesson should be included
                    include_lesson = False
                    
                    if course_option == "Private Swim Lessons":
                        # Direct date match
                        if start_date == target_date:
                            include_lesson = True
                    elif course_option == "Swim Lessons - Private Package (4 pack)":
                        # Check if it's 0, 7, 14, or 21 days after start date
                        days_diff = (target_date - start_date).days
                        if days_diff in [0, 7, 14, 21]:
                            include_lesson = True
                    
                    if include_lesson:
                        # Check if start time is in the correct session
                        if start_time_str and start_time_str != 'nan':
                            try:
                                # Parse time and check session
                                if ':' in start_time_str:
                                    time_parts = start_time_str.split(':')
                                    hour_str = time_parts[0].strip()
                                    minute_str = time_parts[1].split()[0].strip() if ' ' in time_parts[1] else time_parts[1].strip()
                                    
                                    hour = int(hour_str)
                                    minute = int(minute_str)
                                    
                                    # Convert to 24-hour format if needed
                                    if 'PM' in start_time_str.upper() and hour != 12:
                                        hour += 12
                                    elif 'AM' in start_time_str.upper() and hour == 12:
                                        hour = 0
                                    
                                    # Check if time is in the correct session
                                    if session_mode == "AM":
                                        # AM session: 8:20-12:45
                                        if 8 <= hour <= 12:
                                            first_name = str(row.get('First Name', '')).strip()
                                            age = str(row.get('Age', '')).strip()
                                            
                                            private_lessons.append({
                                                'first_name': first_name,
                                                'age': age,
                                                'start_date': start_date,
                                                'start_time': f"{hour:02d}:{minute:02d}"
                                            })
                                    elif session_mode == "PM":
                                        # PM session: 3:45-8:00
                                        if hour >= 15 or hour < 8:
                                            first_name = str(row.get('First Name', '')).strip()
                                            age = str(row.get('Age', '')).strip()
                                            
                                            private_lessons.append({
                                                'first_name': first_name,
                                                'age': age,
                                                'start_date': start_date,
                                                'start_time': f"{hour:02d}:{minute:02d}"
                                            })
                            except (ValueError, IndexError):
                                continue
                        
                except (ValueError, TypeError):
                    continue
            
            return private_lessons
            
        except Exception as e:
            print(f"Error parsing private lessons: {e}")
            return []
    
    def generate_schedule_template(self, group_classes, private_lessons, session_mode):
        """Generate schedule template from parsed enrollment data"""
        try:
            # Load the blank template
            template_path = "assets/Blank_MTWT_Template1.xlsx"
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template file not found: {template_path}")
            
            wb = load_workbook(template_path)
            ws = wb.active
            
            # Get time slots based on session mode
            time_slots = self.am_times if session_mode == "AM" else self.pm_times
            
            # Clear existing content (except headers)
            for row in range(2, ws.max_row + 1):
                for col in range(2, ws.max_column + 1):
                    ws.cell(row=row, column=col, value="")
            
            # Update time column
            for i, time_slot in enumerate(time_slots):
                if i + 2 <= ws.max_row:
                    ws.cell(row=i + 2, column=1, value=time_slot)
            
            # Get headers to map class types to columns
            headers = [ws.cell(row=1, column=col).value for col in range(1, ws.max_column + 1)]
            header_to_col = {header: col for col, header in enumerate(headers, 1)}
            
            # Process group classes
            for class_info in group_classes:
                class_type = class_info['class_type']
                start_time = class_info['start_time']
                enrollment = class_info['enrollment']
                
                # Find the time slot row
                time_row = None
                for i, time_slot in enumerate(time_slots):
                    if time_slot == start_time:
                        time_row = i + 2
                        break
                
                if time_row and class_type in header_to_col:
                    col = header_to_col[class_type]
                    ws.cell(row=time_row, column=col, value=enrollment)
            
            # Process private lessons with time-based placement
            if private_lessons and 'PSL' in header_to_col:
                psl_col = header_to_col['PSL']
                
                # Group private lessons by their actual start times
                psl_by_time = {}
                for lesson in private_lessons:
                    start_time = lesson.get('start_time', '')
                    if start_time in time_slots:
                        if start_time not in psl_by_time:
                            psl_by_time[start_time] = []
                        psl_by_time[start_time].append(f"{lesson['first_name']} ({lesson['age']})")
                
                # Place private lessons at their actual times
                for time_slot in time_slots:
                    if time_slot in psl_by_time:
                        time_row = time_slots.index(time_slot) + 2
                        if time_row <= ws.max_row:
                            ws.cell(row=time_row, column=psl_col, value='; '.join(psl_by_time[time_slot]))
            
            # Save the template
            wb.save(template_path)
            return True
            
        except Exception as e:
            print(f"Error generating schedule template: {e}")
            return False
    
    def get_template_preview(self, group_classes, private_lessons, session_mode):
        """Generate a preview of the schedule template"""
        try:
            # Create a preview DataFrame with all standard columns
            time_slots = self.am_times if session_mode == "AM" else self.pm_times
            
            # Define all columns in the correct order (matching template format)
            all_columns = [
                'Time', 'Starters', 'P1', 'P2', 'P3', 'Y1', 'Y2', 'Y3', 'PSL',
                'STRK4', 'STRK5', 'STRK6', 'TN/AD BSCS', 'TN/AD STRKS', 'CNDTNG', 'brk'
            ]
            
            # Create DataFrame
            preview_data = {col: [''] * len(time_slots) for col in all_columns}
            preview_data['Time'] = time_slots
            
            # Fill in group classes
            for class_info in group_classes:
                class_type = class_info['class_type']
                start_time = class_info['start_time']
                enrollment = class_info['enrollment']
                
                if class_type in preview_data and start_time in time_slots:
                    time_idx = time_slots.index(start_time)
                    preview_data[class_type][time_idx] = enrollment
            
            # Fill in private lessons with time-based distribution
            if private_lessons:
                # Group private lessons by time
                psl_by_time = {}
                for lesson in private_lessons:
                    start_time = lesson.get('start_time', '')
                    if start_time in time_slots:
                        if start_time not in psl_by_time:
                            psl_by_time[start_time] = []
                        psl_by_time[start_time].append(f"{lesson['first_name']} ({lesson['age']})")
                
                # Fill PSL column based on actual times
                for time_slot in time_slots:
                    if time_slot in psl_by_time:
                        time_idx = time_slots.index(time_slot)
                        preview_data['PSL'][time_idx] = '; '.join(psl_by_time[time_slot])
            
            return pd.DataFrame(preview_data)
            
        except Exception as e:
            print(f"Error generating preview: {e}")
            return pd.DataFrame() 