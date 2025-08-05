# instructor_manager.py - Instructor Profile Management

import json
import os
from datetime import time
from typing import List, Dict, Optional

class InstructorManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.instructors_file = os.path.join(data_dir, "instructors.json")
        self._ensure_data_dir()
        self._load_instructors()
    
    def _ensure_data_dir(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_instructors(self):
        """Load instructors from JSON file"""
        if os.path.exists(self.instructors_file):
            try:
                with open(self.instructors_file, 'r') as f:
                    self.instructors = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.instructors = []
        else:
            self.instructors = []
    
    def _save_instructors(self):
        """Save instructors to JSON file"""
        with open(self.instructors_file, 'w') as f:
            json.dump(self.instructors, f, indent=2, default=str)
    
    def get_all_instructors(self) -> List[Dict]:
        """Get all instructor profiles"""
        return self.instructors
    
    def get_instructor_by_name(self, name: str) -> Optional[Dict]:
        """Get instructor profile by name"""
        for instructor in self.instructors:
            if instructor['name'].lower() == name.lower():
                return instructor
        return None
    
    def add_instructor(self, name: str, role: str, cant_teach: List[str], 
                      default_start_time: time = None, default_end_time: time = None) -> bool:
        """Add a new instructor profile"""
        # Check if instructor already exists
        if self.get_instructor_by_name(name):
            return False
        
        instructor = {
            'name': name,
            'role': role,
            'cant_teach': cant_teach,
            'default_start_time': default_start_time.isoformat() if default_start_time else None,
            'default_end_time': default_end_time.isoformat() if default_end_time else None
        }
        
        self.instructors.append(instructor)
        self._save_instructors()
        return True
    
    def update_instructor(self, name: str, role: str, cant_teach: List[str],
                        default_start_time: time = None, default_end_time: time = None) -> bool:
        """Update an existing instructor profile"""
        instructor = self.get_instructor_by_name(name)
        if not instructor:
            return False
        
        instructor['role'] = role
        instructor['cant_teach'] = cant_teach
        instructor['default_start_time'] = default_start_time.isoformat() if default_start_time else None
        instructor['default_end_time'] = default_end_time.isoformat() if default_end_time else None
        
        self._save_instructors()
        return True
    
    def delete_instructor(self, name: str) -> bool:
        """Delete an instructor profile"""
        instructor = self.get_instructor_by_name(name)
        if not instructor:
            return False
        
        self.instructors.remove(instructor)
        self._save_instructors()
        return True
    
    def get_instructor_names(self) -> List[str]:
        """Get list of all instructor names"""
        return [instructor['name'] for instructor in self.instructors]
    
    def get_available_classes(self) -> List[str]:
        """Get list of available class types for preferences"""
        return [
            "Starters", "P1", "P2", "P3", "Y1", "Y2", "Y3", "PSL",
            "STRK4", "STRK5", "STRK6", "TN BCS AD BCS", "TN STRK AD STRK",
            "TN/AD BSCS", "TN/AD STRKS", "CNDTNG"
        ]

# Global instructor manager instance
instructor_manager = InstructorManager() 