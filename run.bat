@echo off
echo 🚀 Starting PDF Chat Application...
echo.

REM Check if virtual environment exists
if not exist "pdf_chat_env" (
    echo 📦 Creating virtual environment...
    python -m venv pdf_chat_env
    echo ✅ Virtual environment created!
    echo.
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call pdf_chat_env\Scripts\activate

REM Install requirements
echo 📥 Installing/updating dependencies...
pip install -r requirements.txt

REM Run the application
echo.
echo 🎉 Starting PDF Chat App...
echo 🌐 The app will open in your browser automatically
echo 📱 URL: http://localhost:8501
echo.
echo ⏹️ Press Ctrl+C to stop the application
echo.

streamlit run app.py

pause
