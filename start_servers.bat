echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "cd /d d:\VS Code\bot\chatbot && .\.venv\Scripts\activate && python backend\rag_api_server.py"

timeout /t 3 /nobreak > nul

echo 🌐 Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d d:\VS Code\bot\chatbot\frontend && python -m http.server 3000"

echo.
echo ✅ Servers started!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:5000
echo.
echo Press any key to exit...
pause > nul
