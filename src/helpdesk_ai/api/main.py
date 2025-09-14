"""
FastAPI backend for Help Desk AI Chat-Bot.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from helpdesk_ai.models.chatbot import HelpDeskChatBot
from helpdesk_ai.core.automation import HelpDeskAutomation, TicketPriority

# Initialize FastAPI app
app = FastAPI(
    title="Help Desk AI API",
    description="AI-powered help desk with RAG and knowledge base learning",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
chatbot = None
helpdesk = None

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    use_rag: bool = True

class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None

class TicketCreate(BaseModel):
    title: str
    description: str
    user_id: str
    priority: str = "medium"

class TicketMessage(BaseModel):
    ticket_id: str
    message: str
    user_id: str

class KnowledgeJSON(BaseModel):
    data: Dict[str, Any]
    category: str = "general"

class KnowledgeText(BaseModel):
    text: str
    category: str = "general"
    metadata: Optional[Dict[str, Any]] = None

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

# Dependency to get chatbot instance
async def get_chatbot():
    global chatbot
    if chatbot is None:
        chatbot = HelpDeskChatBot()
    return chatbot

# Dependency to get helpdesk instance
async def get_helpdesk():
    global helpdesk, chatbot
    if helpdesk is None:
        if chatbot is None:
            chatbot = HelpDeskChatBot()
        helpdesk = HelpDeskAutomation(chatbot)
    return helpdesk

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global chatbot, helpdesk
    print("Initializing Help Desk AI services...")
    chatbot = HelpDeskChatBot()
    helpdesk = HelpDeskAutomation(chatbot)
    print("Services initialized successfully!")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Help Desk AI API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "chatbot_ready": chatbot is not None,
        "helpdesk_ready": helpdesk is not None
    }

# Chat endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, bot: HelpDeskChatBot = Depends(get_chatbot)):
    """Chat with the AI assistant."""
    try:
        response = bot.chat(message.message, message.use_rag)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history")
async def get_chat_history(bot: HelpDeskChatBot = Depends(get_chatbot)):
    """Get chat history."""
    try:
        history = bot.get_conversation_history()
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat/history")
async def clear_chat_history(bot: HelpDeskChatBot = Depends(get_chatbot)):
    """Clear chat history."""
    try:
        bot.clear_conversation_history()
        return {"message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ticket endpoints
@app.post("/tickets")
async def create_ticket(ticket_data: TicketCreate, desk: HelpDeskAutomation = Depends(get_helpdesk)):
    """Create a new ticket."""
    try:
        ticket = desk.create_ticket(
            ticket_data.title,
            ticket_data.description,
            ticket_data.user_id,
            ticket_data.priority
        )
        return {"ticket": ticket.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str, desk: HelpDeskAutomation = Depends(get_helpdesk)):
    """Get ticket by ID."""
    try:
        ticket = desk.get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return {"ticket": ticket.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets")
async def list_tickets(
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    desk: HelpDeskAutomation = Depends(get_helpdesk)
):
    """List tickets with optional filters."""
    try:
        tickets = desk.list_tickets(status=status, user_id=user_id)
        return {
            "tickets": [ticket.to_dict() for ticket in tickets],
            "count": len(tickets)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tickets/message")
async def send_ticket_message(
    message_data: TicketMessage,
    desk: HelpDeskAutomation = Depends(get_helpdesk)
):
    """Send message to a ticket."""
    try:
        response = desk.process_ticket_message(
            message_data.ticket_id,
            message_data.message,
            message_data.user_id
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets/stats")
async def get_ticket_stats(desk: HelpDeskAutomation = Depends(get_helpdesk)):
    """Get ticket statistics."""
    try:
        stats = desk.get_ticket_statistics()
        return {"statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Knowledge base endpoints
@app.post("/knowledge/json")
async def add_json_knowledge(
    knowledge: KnowledgeJSON,
    bot: HelpDeskChatBot = Depends(get_chatbot)
):
    """Add JSON data to knowledge base."""
    try:
        bot.add_knowledge_from_json(knowledge.data, knowledge.category)
        return {"message": "JSON knowledge added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge/text")
async def add_text_knowledge(
    knowledge: KnowledgeText,
    bot: HelpDeskChatBot = Depends(get_chatbot)
):
    """Add text to knowledge base."""
    try:
        metadata = knowledge.metadata or {"category": knowledge.category}
        bot.add_knowledge_from_text(knowledge.text, metadata)
        return {"message": "Text knowledge added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge/search")
async def search_knowledge(
    search: SearchQuery,
    bot: HelpDeskChatBot = Depends(get_chatbot)
):
    """Search knowledge base."""
    try:
        results = bot.search_knowledge(search.query, search.top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge/stats")
async def get_knowledge_stats(bot: HelpDeskChatBot = Depends(get_chatbot)):
    """Get knowledge base statistics."""
    try:
        stats = bot.get_knowledge_stats()
        return {"statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System endpoints
@app.get("/system/info")
async def get_system_info():
    """Get system information."""
    try:
        import torch
        import transformers
        
        return {
            "python_version": sys.version,
            "pytorch_version": torch.__version__,
            "transformers_version": transformers.__version__,
            "cuda_available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/status")
async def get_system_status():
    """Get system status."""
    try:
        chatbot_ready = chatbot is not None
        helpdesk_ready = helpdesk is not None
        
        model_loaded = False
        if chatbot_ready:
            model_loaded = chatbot.pipeline is not None
        
        return {
            "chatbot_ready": chatbot_ready,
            "helpdesk_ready": helpdesk_ready,
            "model_loaded": model_loaded,
            "overall_status": "ready" if all([chatbot_ready, helpdesk_ready, model_loaded]) else "initializing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )