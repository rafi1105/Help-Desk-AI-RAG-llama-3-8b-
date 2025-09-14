#!/usr/bin/env python3
"""
Setup script for Help Desk AI RAG system.
Initializes the system with sample data and configurations.
"""
import os
import sys
import json
import argparse

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from helpdesk_ai.models.chatbot import HelpDeskChatBot
from helpdesk_ai.core.automation import HelpDeskAutomation
from helpdesk_ai.utils.helpers import (
    load_sample_knowledge_base, 
    create_sample_tickets,
    setup_logging,
    ensure_directory_exists
)

def setup_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "vector_db",
        "knowledge_base",
        "logs"
    ]
    
    for directory in directories:
        ensure_directory_exists(directory)
        print(f"✓ Created directory: {directory}")

def initialize_knowledge_base(chatbot, use_sample=True):
    """Initialize knowledge base with sample data."""
    print("Initializing knowledge base...")
    
    if use_sample:
        # Load sample FAQ data
        sample_data = load_sample_knowledge_base()
        for item in sample_data:
            chatbot.add_knowledge_from_json(item, item.get("category", "general"))
        print(f"✓ Added {len(sample_data)} sample FAQ items")
    
    # Load knowledge base file if exists
    kb_file = "knowledge_base/sample_faq.json"
    if os.path.exists(kb_file):
        try:
            with open(kb_file, 'r') as f:
                faq_data = json.load(f)
            
            for item in faq_data:
                chatbot.add_knowledge_from_json(item, item.get("category", "general"))
            print(f"✓ Loaded {len(faq_data)} items from {kb_file}")
        except Exception as e:
            print(f"⚠ Error loading {kb_file}: {e}")
    
    # Save knowledge base
    chatbot.knowledge_base.save_knowledge_base()
    print("✓ Knowledge base saved")

def create_sample_data(helpdesk):
    """Create sample tickets for demonstration."""
    print("Creating sample tickets...")
    
    sample_tickets = create_sample_tickets()
    created_tickets = []
    
    for ticket_data in sample_tickets:
        ticket = helpdesk.create_ticket(
            ticket_data["title"],
            ticket_data["description"],
            ticket_data["user_id"],
            ticket_data["priority"]
        )
        created_tickets.append(ticket)
    
    print(f"✓ Created {len(created_tickets)} sample tickets")
    return created_tickets

def test_system(chatbot, helpdesk):
    """Test the system functionality."""
    print("Testing system functionality...")
    
    # Test chatbot
    test_message = "How do I reset my password?"
    response = chatbot.chat(test_message)
    print(f"✓ Chatbot test successful")
    print(f"  Q: {test_message}")
    print(f"  A: {response[:100]}...")
    
    # Test knowledge search
    search_results = chatbot.search_knowledge("password reset", top_k=3)
    print(f"✓ Knowledge search test successful ({len(search_results)} results)")
    
    # Test ticket system
    test_ticket = helpdesk.create_ticket(
        "Test ticket",
        "This is a test ticket for system verification",
        "test_user",
        "low"
    )
    print(f"✓ Ticket system test successful (ID: {test_ticket.id[:8]}...)")
    
    # Get statistics
    kb_stats = chatbot.get_knowledge_stats()
    ticket_stats = helpdesk.get_ticket_statistics()
    
    print(f"✓ System statistics:")
    print(f"  - Knowledge documents: {kb_stats.get('total_documents', 0)}")
    print(f"  - Total tickets: {ticket_stats.get('total_tickets', 0)}")

def create_config_file():
    """Create a sample configuration file."""
    config_content = """# Help Desk AI Configuration
# Copy this to .env and update with your settings

# Hugging Face token for accessing Llama models (required for some models)
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
"""
    
    with open(".env.example", "w") as f:
        f.write(config_content)
    
    print("✓ Created .env.example configuration file")

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup Help Desk AI RAG system")
    parser.add_argument("--no-sample-data", action="store_true", 
                       help="Skip creating sample data")
    parser.add_argument("--quick", action="store_true",
                       help="Quick setup without model initialization")
    args = parser.parse_args()
    
    print("🚀 Setting up Help Desk AI RAG system...")
    print("=" * 50)
    
    # Setup logging
    logger = setup_logging()
    
    # Create directories
    setup_directories()
    
    # Create config file
    create_config_file()
    
    if args.quick:
        print("✓ Quick setup completed!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the system: python -m streamlit run src/helpdesk_ai/ui/streamlit_app.py")
        return
    
    try:
        # Initialize chatbot (this may take time)
        print("\n📦 Initializing AI models...")
        print("⚠ This may take several minutes on first run...")
        chatbot = HelpDeskChatBot()
        
        # Initialize help desk
        helpdesk = HelpDeskAutomation(chatbot)
        
        # Setup knowledge base
        initialize_knowledge_base(chatbot, use_sample=not args.no_sample_data)
        
        # Create sample data
        if not args.no_sample_data:
            create_sample_data(helpdesk)
        
        # Test system
        test_system(chatbot, helpdesk)
        
        print("\n🎉 Setup completed successfully!")
        print("=" * 50)
        print("\nYour Help Desk AI system is ready!")
        print("\nTo start the web interface:")
        print("  streamlit run src/helpdesk_ai/ui/streamlit_app.py")
        print("\nTo start the API server:")
        print("  python src/helpdesk_ai/api/main.py")
        print("\nTo start with Uvicorn:")
        print("  uvicorn src.helpdesk_ai.api.main:app --reload")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nTry running with --quick flag for minimal setup")
        print("Then manually configure the system")
        sys.exit(1)

if __name__ == "__main__":
    main()