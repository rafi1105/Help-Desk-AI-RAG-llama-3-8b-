# Help Desk AI RAG Chat-Bot 🤖

An advanced AI-powered help desk automation system using Llama 3 8B with Retrieval-Augmented Generation (RAG) capabilities. This system provides intelligent customer support through automated ticket handling, knowledge base learning, and chat-bot assistance.

## 🌟 Features

- **🤖 AI Chat-Bot**: Powered by Llama 3 8B for intelligent conversations
- **📚 RAG System**: Retrieval-Augmented Generation for accurate, context-aware responses
- **🎫 Ticket Management**: Automated help desk ticket creation and management
- **📊 Knowledge Base**: JSON data processing and dynamic learning capabilities
- **🌐 Web Interface**: User-friendly Streamlit web application
- **🔗 REST API**: FastAPI backend for integration with other systems
- **📈 Analytics**: Comprehensive statistics and performance tracking
- **🔍 Smart Search**: Vector-based semantic search in knowledge base
- **🎯 Auto-Resolution**: Intelligent ticket resolution detection
- **📝 Learning System**: Continuous learning from user interactions

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (recommended for Llama 3 8B)
- 16GB+ RAM recommended

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/rafi1105/Help-Desk-AI-RAG-llama-3-8b-.git
cd Help-Desk-AI-RAG-llama-3-8b-
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure the system:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the setup script:**
```bash
python setup.py
```

5. **Start the web interface:**
```bash
streamlit run src/helpdesk_ai/ui/streamlit_app.py
```

## 🔧 Configuration

Create a `.env` file with your configuration:

```env
# Hugging Face token for accessing Llama models
HUGGINGFACE_TOKEN=your_token_here

# Model configuration
MODEL_NAME=meta-llama/Meta-Llama-3-8B-Instruct
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Storage paths
VECTOR_DB_PATH=./vector_db
KNOWLEDGE_BASE_PATH=./knowledge_base

# Generation parameters
MAX_TOKENS=512
TEMPERATURE=0.7
TOP_K=5

# System settings
DEVICE=auto
DEBUG_MODE=false
```

## 💻 Usage

### Web Interface

1. Start the Streamlit app:
```bash
streamlit run src/helpdesk_ai/ui/streamlit_app.py
```

2. Open your browser to `http://localhost:8501`

3. Features available:
   - **Chat Interface**: Direct conversation with AI
   - **Ticket Management**: Create and manage support tickets
   - **Knowledge Base**: Add and search knowledge documents
   - **Settings**: System configuration and data management

### API Server

1. Start the FastAPI server:
```bash
python src/helpdesk_ai/api/main.py
```

2. Access the API documentation at `http://localhost:8000/docs`

### API Examples

**Chat with the AI:**
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "How do I reset my password?", "use_rag": true}'
```

**Create a ticket:**
```bash
curl -X POST "http://localhost:8000/tickets" \
     -H "Content-Type: application/json" \
     -d '{"title": "Login Issue", "description": "Cannot access account", "user_id": "user123", "priority": "high"}'
```

**Add knowledge:**
```bash
curl -X POST "http://localhost:8000/knowledge/json" \
     -H "Content-Type: application/json" \
     -d '{"data": {"question": "How to...", "answer": "To do this..."}, "category": "help"}'
```

## 🏗️ Architecture

```
Help-Desk-AI-RAG-llama-3-8b-/
├── src/helpdesk_ai/
│   ├── core/                 # Core system components
│   │   ├── config.py        # Configuration management
│   │   ├── knowledge_base.py # RAG knowledge base
│   │   └── automation.py    # Help desk automation
│   ├── models/              # AI models
│   │   └── chatbot.py       # Llama 3 8B chat-bot
│   ├── api/                 # FastAPI backend
│   │   └── main.py          # API endpoints
│   ├── ui/                  # User interface
│   │   └── streamlit_app.py # Streamlit web app
│   └── utils/               # Utility functions
│       └── helpers.py       # Helper functions
├── knowledge_base/          # Knowledge base files
├── data/                    # Ticket and user data
├── vector_db/               # Vector embeddings
└── requirements.txt         # Python dependencies
```

## 🧠 How It Works

### RAG System
1. **Document Processing**: JSON data and text documents are processed and embedded
2. **Vector Storage**: Embeddings stored in FAISS vector database
3. **Semantic Search**: User queries are embedded and matched against knowledge base
4. **Context Retrieval**: Relevant documents retrieved for response generation
5. **Response Generation**: Llama 3 8B generates responses using retrieved context

### Help Desk Automation
1. **Ticket Creation**: Users create tickets through web UI or API
2. **Auto-Response**: AI generates initial responses based on ticket content
3. **Conversation Management**: Ongoing conversation tracked per ticket
4. **Learning**: System learns from successful resolutions
5. **Auto-Resolution**: Tickets automatically resolved when user confirms solution

### Knowledge Base Learning
1. **Interaction Capture**: All user interactions captured and analyzed
2. **Quality Assessment**: Successful Q&A pairs identified
3. **Knowledge Extraction**: New knowledge extracted from conversations
4. **Continuous Improvement**: Knowledge base continuously updated

## 📊 Features in Detail

### Chat-Bot Capabilities
- Natural language understanding and generation
- Context-aware responses using RAG
- Conversation history management
- Fallback to smaller models if needed
- Support for multiple conversation threads

### Ticket Management
- Priority-based ticket handling
- Status tracking and updates
- Message threading
- Auto-resolution detection
- Performance analytics

### Knowledge Base
- JSON data processing
- Text document indexing
- Semantic search capabilities
- Category-based organization
- Version control and backup

## 🔒 Security & Privacy

- No sensitive data stored in embeddings
- Conversation data can be cleared
- Local deployment option available
- API authentication support (configurable)
- Data export capabilities

## 🛠️ Development

### Running Tests
```bash
# Basic functionality test
python setup.py --quick

# Full system test
python setup.py
```

### Adding Custom Knowledge
```python
from helpdesk_ai.models.chatbot import HelpDeskChatBot

chatbot = HelpDeskChatBot()

# Add JSON knowledge
knowledge = {
    "question": "Custom question?",
    "answer": "Custom answer...",
    "category": "custom"
}
chatbot.add_knowledge_from_json(knowledge, "custom")

# Add text knowledge
chatbot.add_knowledge_from_text(
    "This is custom knowledge content",
    {"category": "custom", "source": "manual"}
)
```

## 📈 Performance

- **Model**: Llama 3 8B (requires significant compute)
- **Fallback**: Smaller models for resource-constrained environments
- **Response Time**: 2-5 seconds depending on hardware
- **Scalability**: Horizontal scaling supported via API
- **Memory**: 16GB+ recommended for optimal performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♀️ Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Check the `/docs` folder for detailed documentation
- **API Docs**: Available at `http://localhost:8000/docs` when running the API

## 🔄 Updates

- **v1.0.0**: Initial release with Llama 3 8B integration
- RAG-based knowledge retrieval
- Streamlit web interface
- FastAPI backend
- Ticket management system

---

**Note**: This system requires a Hugging Face token to access Llama 3 8B. Ensure you have the necessary permissions and agree to the model's usage terms. 
