# Start LLaMA 3.2 RAG API Server
Write-Host "🚀 Starting LLaMA 3.2 RAG API Server..." -ForegroundColor Green
Write-Host ""

# Set working directory
Set-Location "d:\VS Code\bot\chatbot"

# Check if Ollama is running
Write-Host "🔍 Checking if Ollama is running..." -ForegroundColor Yellow
try {
    $ollamaCheck = ollama list 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Ollama not running"
    }
} catch {
    Write-Host "❌ Ollama is not running. Please start Ollama first:" -ForegroundColor Red
    Write-Host "   1. Open a new terminal" -ForegroundColor White
    Write-Host "   2. Run: ollama serve" -ForegroundColor White
    Write-Host "   3. In another terminal, run: ollama pull llama3.2:1b" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if the model is available
Write-Host "🔍 Checking if llama3.2:1b model is available..." -ForegroundColor Yellow
$modelCheck = ollama list | Select-String "llama3.2:1b"
if (-not $modelCheck) {
    Write-Host "⚠️  llama3.2:1b model not found. Pulling it now..." -ForegroundColor Yellow
    ollama pull llama3.2:1b
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to pull llama3.2:1b model" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "✅ Ollama and model are ready!" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Start the RAG API server
Write-Host "🌐 Starting RAG API Server on port 5000..." -ForegroundColor Cyan
python backend/rag_api_server.py

Read-Host "Press Enter to exit"
