@echo off
echo Starting Aqua Scheduler Pro...
echo.
echo Activating virtual environment...
call venv\Scripts\activate
echo.
echo Starting Streamlit app...
streamlit run app.py
pause

