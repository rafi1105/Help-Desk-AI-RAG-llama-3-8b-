#!/usr/bin/env python3
"""
Demo script for Help Desk AI RAG Chat-Bot.
Shows key features without requiring full setup.
"""
import json
import os

def show_project_overview():
    """Show project overview and features."""
    print("🤖 Help Desk AI RAG Chat-Bot Demo")
    print("=" * 50)
    
    print("\n📋 Project Features:")
    features = [
        "🤖 AI Chat-Bot powered by Llama 3 8B",
        "📚 RAG (Retrieval-Augmented Generation) system",
        "🎫 Automated ticket management",
        "📊 JSON-based knowledge base",
        "🌐 Streamlit web interface",
        "🔗 FastAPI REST API",
        "📈 Learning from interactions",
        "🔍 Semantic search capabilities",
        "🎯 Auto-resolution detection",
        "📝 Continuous knowledge base improvement"
    ]
    
    for feature in features:
        print(f"  {feature}")

def show_architecture():
    """Show system architecture."""
    print("\n🏗️ System Architecture:")
    print("  ┌─────────────────┐")
    print("  │   Web UI        │ ← Streamlit Interface")
    print("  │   (Streamlit)   │")
    print("  └─────────────────┘")
    print("           │")
    print("  ┌─────────────────┐")
    print("  │   API Layer     │ ← FastAPI Backend")
    print("  │   (FastAPI)     │")
    print("  └─────────────────┘")
    print("           │")
    print("  ┌─────────────────┐")
    print("  │   Chat-Bot      │ ← Llama 3 8B Model")
    print("  │   (Llama 3)     │")
    print("  └─────────────────┘")
    print("           │")
    print("  ┌─────────────────┐")
    print("  │   RAG System    │ ← Knowledge Retrieval")
    print("  │   (FAISS)       │")
    print("  └─────────────────┘")
    print("           │")
    print("  ┌─────────────────┐")
    print("  │   Knowledge DB  │ ← Vector Embeddings")
    print("  │   (Embeddings)  │")
    print("  └─────────────────┘")

def show_sample_data():
    """Show sample knowledge base data."""
    print("\n📚 Sample Knowledge Base:")
    
    if os.path.isfile("knowledge_base/sample_faq.json"):
        with open("knowledge_base/sample_faq.json", "r") as f:
            faq_data = json.load(f)
        
        print(f"  Total FAQ items: {len(faq_data)}")
        
        categories = {}
        for item in faq_data:
            cat = item.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        print("  Categories:")
        for cat, count in categories.items():
            print(f"    • {cat}: {count} items")
        
        print("\n  Sample Q&A:")
        for i, item in enumerate(faq_data[:3], 1):
            print(f"    {i}. Q: {item['question']}")
            print(f"       A: {item['answer'][:80]}...")
            print()
    else:
        print("  No sample data found")

def show_api_endpoints():
    """Show available API endpoints."""
    print("\n🔗 API Endpoints:")
    endpoints = [
        ("POST /chat", "Chat with AI assistant"),
        ("GET /chat/history", "Get conversation history"),
        ("POST /tickets", "Create new ticket"),
        ("GET /tickets/{id}", "Get ticket details"),
        ("POST /tickets/message", "Send message to ticket"),
        ("POST /knowledge/json", "Add JSON knowledge"),
        ("POST /knowledge/text", "Add text knowledge"),
        ("POST /knowledge/search", "Search knowledge base"),
        ("GET /system/status", "System health check")
    ]
    
    for endpoint, description in endpoints:
        print(f"  {endpoint:<25} - {description}")

def show_usage_examples():
    """Show usage examples."""
    print("\n💡 Usage Examples:")
    
    print("\n  1. Start Web Interface:")
    print("     streamlit run src/helpdesk_ai/ui/streamlit_app.py")
    
    print("\n  2. Start API Server:")
    print("     python src/helpdesk_ai/api/main.py")
    
    print("\n  3. Command Line Interface:")
    print("     python cli.py --mode chat")
    print("     python cli.py --mode ticket")
    print("     python cli.py --mode knowledge")
    
    print("\n  4. API Usage (curl examples):")
    print("     # Chat with AI")
    print('     curl -X POST "http://localhost:8000/chat" \\')
    print('          -H "Content-Type: application/json" \\')
    print('          -d \'{"message": "How do I reset my password?"}\'')
    
    print("\n     # Create ticket")
    print('     curl -X POST "http://localhost:8000/tickets" \\')
    print('          -H "Content-Type: application/json" \\')
    print('          -d \'{"title": "Login Issue", "description": "Cannot access account", "user_id": "user123"}\'')

def show_setup_instructions():
    """Show setup instructions."""
    print("\n🚀 Quick Setup:")
    print("  1. Install dependencies:")
    print("     pip install -r requirements.txt")
    
    print("\n  2. Configure environment:")
    print("     cp .env.example .env")
    print("     # Edit .env with your settings")
    
    print("\n  3. Initialize system:")
    print("     python setup.py")
    
    print("\n  4. Start the application:")
    print("     streamlit run src/helpdesk_ai/ui/streamlit_app.py")
    
    print("\n⚠️  Note: Llama 3 8B requires:")
    print("     • CUDA-compatible GPU (recommended)")
    print("     • 16GB+ RAM")
    print("     • Hugging Face token for model access")

def main():
    """Main demo function."""
    show_project_overview()
    show_architecture()
    show_sample_data()
    show_api_endpoints()
    show_usage_examples()
    show_setup_instructions()
    
    print("\n" + "=" * 50)
    print("🎉 Help Desk AI RAG Chat-Bot")
    print("Ready to revolutionize your customer support! 🚀")
    print("=" * 50)

if __name__ == "__main__":
    main()