# GreenBot - AI Chatbot for Green University

A professional AI chatbot powered by LLaMA 3.2 and RAG (Retrieval-Augmented Generation) for Green University of Bangladesh.

## 🚀 Quick Start

### Option 1: Automatic Startup (Recommended)
Double-click `start_servers.bat` to automatically start both servers.

### Option 2: Manual Startup
1. **Start Backend Server:**
   ```powershell
   cd "d:\VS Code\bot\chatbot"
   .\.venv\Scripts\activate
   python backend/rag_api_server.py
   ```

2. **Start Frontend Server:**
   ```powershell
   cd "d:\VS Code\bot\chatbot\frontend"
   python -m http.server 3000
   ```

### Option 3: PowerShell Script
Run the PowerShell script:
```powershell
.\backend\run_rag_api_server.ps1
```

## 🌐 Access Your Chatbot

- **Frontend (Web Interface):** http://localhost:3000
- **Backend (API):** http://localhost:5000

## 📋 Prerequisites

1. **Python Virtual Environment** - Already configured
2. **Ollama** - Must be running with LLaMA 3.2:1b model
3. **Data Files** - University information loaded

## 🎯 Features

- 🤖 **AI-Powered Responses** with LLaMA 3.2
- 📚 **University Knowledge Base** with 10,709+ data points
- 💬 **Professional Messenger UI** with dark/light themes
- 📊 **Real-time Analytics** and feedback collection
- 🔄 **Smart Response Methods** (JSON search, LLaMA enhancement)
- 📱 **Responsive Design** for all devices

## 💡 Usage Tips

- Ask about admissions, programs, fees, facilities
- Try questions like: "What programs does Green University offer?"
- Use the feedback buttons to improve responses
- Check analytics in the sidebar for conversation stats

## 🔧 Troubleshooting

**Server shows offline:**
- Ensure both servers are running
- Check that Ollama is running: `ollama serve`
- Verify model is pulled: `ollama pull llama3.2:1b`

**Connection errors:**
- Frontend runs on port 3000
- Backend API runs on port 5000
- Both must be running simultaneously

## 📁 Project Structure

```
chatbot/
├── backend/
│   ├── rag_api_server.py      # Main Flask API server
│   ├── run_rag_api_server.ps1 # PowerShell startup script
│   ├── enhanced_ndata.json     # University data
│   └── green_university_30k_instruction_response.jsonl
├── frontend/
│   ├── index.html             # Main web interface
│   ├── script.js              # Frontend JavaScript
│   └── styles.css             # Custom styles
├── start_servers.bat          # Automatic startup script
└── .venv/                     # Python virtual environment
```

## 🎉 Enjoy Your AI Assistant!

Your GreenBot is now ready to help students and visitors learn about Green University! 🤖✨
