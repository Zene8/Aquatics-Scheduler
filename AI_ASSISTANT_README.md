# 🤖 AI Assistant for Swim Scheduler

## Overview
The AI Assistant provides intelligent help and guidance throughout the swim scheduling process. It includes both contextual tips and a full-featured chatbot.

## Features

### 🎯 Contextual Help Tips
- **Template Upload**: Tips for uploading Excel templates
- **Manual Selection**: Guidance for selecting classes manually
- **Instructor Entry**: Help with adding instructor information
- **Schedule Generation**: Tips for the generation process
- **Download**: Guidance for final steps

### 💬 AI Chatbot
- **Full Conversation**: Ask any questions about the app
- **Quick Help Topics**: Pre-built questions for common tasks
- **Schedule Analysis**: AI-powered schedule review and suggestions
- **Context Awareness**: Remembers conversation history

## Setup

### 1. Get OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to "API Keys" section
4. Create a new API key
5. Copy the key (starts with `sk-`)

### 2. Configure in App
1. Open the "🤖 AI Assistant" tab
2. Enter your API key in the setup section
3. Click "Send" to start chatting

## Usage

### Contextual Tips
- Tips appear automatically throughout the app
- They provide relevant guidance for each step
- No API key required for basic tips

### Chatbot
- Ask questions about any feature
- Get step-by-step guidance
- Request schedule analysis
- Get troubleshooting help

### Quick Help Topics
- **Template Mode**: How to use existing Excel files
- **Manual Mode**: How to create schedules from scratch
- **Instructor Management**: How to manage instructor profiles

## Example Questions

### General Help
- "How do I create a schedule?"
- "What's the difference between AM and PM modes?"
- "How do I manage instructor profiles?"

### Specific Features
- "How does template mode work?"
- "What are the time slots for AM sessions?"
- "How do I set instructor availability?"

### Troubleshooting
- "Why is my schedule empty?"
- "How do I fix instructor conflicts?"
- "What if I can't upload my template?"

## Custom GPT Integration

### Option 1: Use Built-in Assistant
- No additional setup required
- Works directly in the app
- Requires OpenAI API key

### Option 2: Create Custom GPT
1. Go to [ChatGPT](https://chat.openai.com/)
2. Click "Explore GPTs"
3. Create a new GPT with this context:

```
You are an AI assistant for a swim instructor scheduling application. The app helps supervisors create schedules for swim lessons.

APP FEATURES:
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
```

## Benefits

### For Supervisors
- **Faster Learning**: Get help when stuck
- **Better Schedules**: AI suggestions for optimization
- **Reduced Errors**: Guidance prevents mistakes
- **24/7 Support**: Always available help

### For the App
- **Improved UX**: Contextual guidance
- **Reduced Support**: Self-service help
- **Feature Discovery**: Users learn more features
- **Professional Feel**: Modern AI integration

## Technical Details

### Dependencies
- `openai`: For GPT-4 API calls
- `streamlit`: For the chat interface
- `pandas`: For data handling

### Security
- API keys are stored in environment variables
- No persistent storage of sensitive data
- Chat history is session-based only

### Performance
- Cached responses for common questions
- Efficient API usage with token limits
- Graceful error handling for API issues

## Future Enhancements

### Planned Features
- **Voice Input**: Speech-to-text for questions
- **Schedule Optimization**: AI-powered schedule improvements
- **Conflict Resolution**: Automatic conflict detection and suggestions
- **Multi-language Support**: Help in different languages
- **Integration with Calendar**: Sync with external calendars

### Advanced AI Features
- **Predictive Scheduling**: Suggest optimal instructor assignments
- **Workload Balancing**: AI-driven workload distribution
- **Trend Analysis**: Learn from past schedules
- **Automated Reports**: Generate insights automatically 