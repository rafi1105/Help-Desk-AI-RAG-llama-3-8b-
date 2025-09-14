@echo off
echo 🚀 Starting LLaMA 3.2 RAG API Server...
echo.

cd /d "d:\VS Code\GreentBot"

REM Check if Ollama is running
echo 🔍 Checking if Ollama is running...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama is not running. Please start Ollama first:
    echo    1. Open a new terminal
    echo    2. Run: ollama serve
    echo    3. In another terminal, run: ollama pull llama3.2:1b
    echo.
    pause
    exit /b 1
)

REM Check if the model is available
echo 🔍 Checking if llama3.2:1b model is available...
ollama list | findstr "llama3.2:1b" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  llama3.2:1b model not found. Pulling it now...
    ollama pull llama3.2:1b
    if %errorlevel% neq 0 (
        echo ❌ Failed to pull llama3.2:1b model
        pause
        exit /b 1
    )
)

echo ✅ Ollama and model are ready!
echo.

REM Start the RAG API server
echo 🌐 Starting RAG API Server on port 8000...
python rag_api_server.py

pause
