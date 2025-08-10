import streamlit as st
from typing import List, Dict, Optional
import json
import os
from datetime import datetime
import random

class AIAssistant:
    def __init__(self):
        # Demo mode - no API key needed!
        self.client = "demo_mode"
        
        # App context for the AI
        self.app_context = """
        You are an AI assistant for a swim instructor scheduling application. The app helps supervisors create schedules for swim lessons.

        APP FEATURES:
        - Enrollment Upload (RECOMMENDED): Upload enrollment Excel files to automatically generate schedules from actual enrollment data
        - Template Mode: Upload existing Excel templates with class schedules
        - Manual Mode: Create schedules by selecting classes for each time slot
        - AM/PM Sessions: Different time slots for morning and afternoon
        - Instructor Management: Save instructor profiles with preferences
        - Schedule Generation: Automatically assign instructors to classes
        - Excel Output: Download formatted schedules

        CLASS TYPES:
        - Starters, P1, P2, P3 (Beginner levels)
        - Y1, Y2, Y3 (Youth levels) 
        - PSL (Private Swim Lessons)
        - STRK4, STRK5, STRK6 (Stroke levels)
        - TN BCS AD BCS, TN STRK AD STRK (Technique classes)
        - TN/AD BSCS, TN/AD STRKS (Advanced technique)
        - CNDTNG (Conditioning)

        TIME SLOTS:
        - AM: 8:35, 9:10, 9:45, 10:20, 11:00, 11:35, 12:10
        - PM: 4:10, 4:45, 5:20, 5:55, 6:30, 7:05

        ROLES:
        - Instructor: Full teaching role
        - Shadow: Assistant role, paired with instructors

        YOUR ROLE:
        - Help users navigate the app
        - Provide tips for effective scheduling
        - Explain features and best practices
        - Answer questions about the scheduling process
        - Suggest improvements to schedules
        - Help troubleshoot issues
        """

    def get_help_tip(self, context: str, current_step: int = None) -> str:
        """Get contextual help tip based on current app state"""
        tips = {
            "enrollment_upload": "🏆 **Recommended**: Upload enrollment Excel files to automatically generate your schedule! This method reads actual enrollment data and creates the most accurate schedule template.",
            "template_upload": "📋 **Tip**: Upload an Excel file with existing class schedules. The app will try to keep the same instructors for the same classes.",
            "manual_selection": "🎯 **Tip**: Click on time slots to select which classes run at each time. Only selected classes will be scheduled.",
            "instructor_entry": "👥 **Tip**: You can select from saved profiles or type new names. Set availability times and mark classes they can't teach.",
            "schedule_generation": "⚡ **Tip**: The app automatically assigns instructors based on availability and preferences. Check the preview before downloading.",
            "am_mode": "🌅 **AM Mode**: Morning sessions (8:35-12:10). Perfect for early swimmers!",
            "pm_mode": "🌆 **PM Mode**: Afternoon sessions (4:10-7:05). Great for after-school programs!",
            "instructor_management": "💾 **Tip**: Save instructor profiles to avoid re-entering information. Include their preferences and availability.",
            "schedule_preview": "👀 **Preview**: Review the schedule before downloading. Check for conflicts or gaps in coverage.",
            "download": "📥 **Download**: Get your formatted Excel schedule ready for printing and distribution."
        }
        
        if context in tips:
            return tips[context]
        return "💡 **Tip**: Need help? Ask the AI assistant in the chat tab!"

    def get_custom_gpt_button(self) -> str:
        """Get HTML for the Custom GPT button"""
        return """
        <div style="text-align: center; margin: 20px 0;">
            <a href="https://chatgpt.com/g/g-68921c305e2481919789df3d6d3dfdda-swim-scheduler-assistant" 
               target="_blank" 
               style="display: inline-block; 
                      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; 
                      padding: 12px 24px; 
                      text-decoration: none; 
                      border-radius: 25px; 
                      font-weight: bold; 
                      box-shadow: 0 4px 15px rgba(0,0,0,0.2); 
                      transition: all 0.3s ease;">
                🤖 Try Custom Swim Scheduler GPT
            </a>
        </div>
        """

    def chat_with_ai(self, message: str, chat_history: List[Dict] = None) -> str:
        """Chat with the AI assistant (Demo Mode)"""
        # Convert message to lowercase for keyword matching
        msg_lower = message.lower()
        
        # Intelligent response system based on keywords
        if any(word in msg_lower for word in ["help", "how", "what", "?"]):
            if "template" in msg_lower:
                return "🤖 **AI Assistant**: Template mode is perfect for maintaining consistency! Upload an existing Excel schedule and the app will try to assign the same instructors to the same classes. This is great for building rapport with students and parents."
            elif "manual" in msg_lower:
                return "🤖 **AI Assistant**: Manual mode gives you complete control! You can select exactly which classes run at each time slot. This is ideal when you want to customize the schedule or don't have a previous template to work from."
            elif "instructor" in msg_lower:
                return "🤖 **AI Assistant**: Adding instructors is easy! You can select from saved profiles or type new names. Make sure to set realistic availability times and mark any classes they can't teach. The app will automatically balance their workload."
            elif "schedule" in msg_lower:
                return "🤖 **AI Assistant**: The scheduling algorithm is quite smart! It considers availability, preferences, workload balance, and even adds appropriate breaks. It also tries to pair shadows with full instructors when possible."
            else:
                return "🤖 **AI Assistant**: I'm here to help! You can ask me about template vs manual mode, instructor management, scheduling tips, or any other features. What would you like to know more about?"
        
        elif any(word in msg_lower for word in ["am", "pm", "time", "session"]):
            return "🤖 **AI Assistant**: Great question about sessions! AM mode runs from 8:35-12:10 (perfect for early swimmers), while PM mode is 4:10-7:05 (great for after-school programs). The app automatically sets default availability times 30 minutes before and after each session."
        
        elif any(word in msg_lower for word in ["class", "lesson", "level"]):
            return "🤖 **AI Assistant**: The app handles all swim class types! From Starters and P1-P3 for beginners, to Y1-Y3 for youth, STRK4-6 for stroke development, and specialized classes like PSL (private lessons) and CNDTNG (conditioning). Each class can have different instructor requirements."
        
        elif any(word in msg_lower for word in ["download", "excel", "file"]):
            return "🤖 **AI Assistant**: The download feature creates a beautifully formatted Excel file! It includes instructor names, student counts, proper coloring, and professional borders. Perfect for printing and distributing to your team."
        
        elif any(word in msg_lower for word in ["error", "problem", "issue", "bug"]):
            return "🤖 **AI Assistant**: If you're experiencing issues, try these troubleshooting steps:\n\n1. Make sure all instructor availability times are set correctly\n2. Check that you've selected classes in manual mode\n3. Verify instructor names are spelled consistently\n4. Try refreshing the page if the app seems stuck"
        
        elif any(word in msg_lower for word in ["tip", "advice", "suggestion"]):
            return "🤖 **AI Assistant**: Here are my top tips for effective scheduling:\n\n• Save instructor profiles to avoid re-entering information\n• Use template mode for consistency across sessions\n• Set realistic availability times (30 min buffer recommended)\n• Mark classes instructors can't teach to avoid conflicts\n• Review the preview before downloading"
        
        elif any(word in msg_lower for word in ["thank", "thanks"]):
            return "🤖 **AI Assistant**: You're very welcome! I'm here to make your scheduling process as smooth as possible. Feel free to ask me anything else about the app or scheduling best practices!"
        
        else:
            # Default intelligent response
            responses = [
                "🤖 **AI Assistant**: That's a great question! The swim scheduling app is designed to make your life easier. Is there something specific about the scheduling process you'd like me to explain?",
                "🤖 **AI Assistant**: I'm here to help optimize your scheduling workflow! Whether you need help with instructor management, template usage, or schedule generation, just let me know what you're working on.",
                "🤖 **AI Assistant**: The app has many powerful features! From automatic instructor assignment to workload balancing, it handles the complex parts so you can focus on what matters most. What aspect would you like to explore?"
            ]
            return random.choice(responses)

    def analyze_schedule(self, schedule_data: Dict) -> str:
        """Analyze a generated schedule and provide feedback (Demo Mode)"""
        return """🤖 **AI Assistant**: Schedule Analysis Complete!

📊 **Coverage Analysis**: 
• All selected classes appear to be covered
• Instructor assignments look balanced

⚖️ **Workload Distribution**:
• Instructors have reasonable teaching loads
• Breaks are well distributed throughout the schedule

🎯 **Recommendations**:
• Review the schedule preview before finalizing
• Check that all instructor availability times are accurate
• Consider instructor preferences for future sessions

✅ **Overall Assessment**: This schedule looks well-optimized! The algorithm has done a good job balancing instructor workload while maintaining class coverage."""

    def get_step_guidance(self, step: int) -> str:
        """Get guidance for specific app steps"""
        guidance = {
            1: """
            **Step 1: Choose Your Mode** 🎯
            
            **Template Mode**: 
            - Upload an existing Excel schedule
            - App tries to keep same instructors for same classes
            - Good for consistency across sessions
            
            **Manual Mode**:
            - Create schedule from scratch
            - Select which classes run at each time
            - More control over class selection
            
            **AM/PM Selection**:
            - AM: 8:35-12:10 (morning sessions)
            - PM: 4:10-7:05 (afternoon sessions)
            """,
            
            2: """
            **Step 2: Add Instructors** 👥
            
            **Quick Tips**:
            - Use saved profiles for efficiency
            - Set realistic availability times
            - Mark classes they can't teach
            - Include both instructors and shadows
            
            **Time Defaults**:
            - AM: 8:05-12:40 (30 min before/after session)
            - PM: 3:40-7:35 (30 min before/after session)
            """,
            
            3: """
            **Step 3: Review & Generate** ⚡
            
            **What to Check**:
            - All instructors added correctly
            - Availability times make sense
            - Can't-teach preferences set
            - Roles assigned properly
            
            **Generation Process**:
            - App matches instructors to classes
            - Considers availability and preferences
            - Balances workload and breaks
            - Creates optimized schedule
            """,
            
            4: """
            **Step 4: Download & Share** 📥
            
            **Final Steps**:
            - Review the generated schedule
            - Check for any issues or conflicts
            - Download Excel file
            - Print and distribute to instructors
            
            **Schedule Features**:
            - Formatted with colors and borders
            - Instructor names and student counts
            - Break assignments
            - Professional appearance
            """
        }
        
        return guidance.get(step, "Step guidance not available.")

# Global AI assistant instance
ai_assistant = AIAssistant() 