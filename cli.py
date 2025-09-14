#!/usr/bin/env python3
"""
Command-line interface for Help Desk AI Chat-Bot.
Simple interface for testing and development.
"""
import sys
import os
import argparse

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from helpdesk_ai.models.chatbot import HelpDeskChatBot
from helpdesk_ai.core.automation import HelpDeskAutomation

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Help Desk AI Chat-Bot CLI")
    parser.add_argument("--mode", choices=["chat", "ticket", "knowledge"], 
                       default="chat", help="Operation mode")
    parser.add_argument("--user-id", default="cli_user", help="User ID")
    args = parser.parse_args()
    
    print("🤖 Help Desk AI Chat-Bot CLI")
    print("=" * 40)
    print("Initializing... Please wait...")
    
    try:
        # Initialize system
        chatbot = HelpDeskChatBot()
        helpdesk = HelpDeskAutomation(chatbot)
        
        print("✓ System initialized successfully!")
        print(f"Mode: {args.mode}")
        print("Type 'quit' to exit, 'help' for commands")
        print("-" * 40)
        
        if args.mode == "chat":
            chat_mode(chatbot)
        elif args.mode == "ticket":
            ticket_mode(helpdesk, args.user_id)
        elif args.mode == "knowledge":
            knowledge_mode(chatbot)
            
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        print("Try running setup.py first")
        sys.exit(1)

def chat_mode(chatbot):
    """Interactive chat mode."""
    print("💬 Chat Mode - Talk directly with the AI")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
            elif user_input.lower() == 'help':
                print("Commands:")
                print("  quit/exit/bye - Exit the program")
                print("  clear - Clear conversation history")
                print("  stats - Show knowledge base statistics")
                continue
            elif user_input.lower() == 'clear':
                chatbot.clear_conversation_history()
                print("✓ Conversation history cleared")
                continue
            elif user_input.lower() == 'stats':
                stats = chatbot.get_knowledge_stats()
                print(f"📊 Knowledge Base: {stats}")
                continue
            elif not user_input:
                continue
            
            print("AI: ", end="", flush=True)
            response = chatbot.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n👋 Goodbye!")

def ticket_mode(helpdesk, user_id):
    """Interactive ticket mode."""
    print(f"🎫 Ticket Mode - User: {user_id}")
    current_ticket = None
    
    while True:
        try:
            if current_ticket is None:
                print("\nOptions:")
                print("1. Create new ticket")
                print("2. List my tickets")
                print("3. Open existing ticket")
                print("4. Quit")
                
                choice = input("Select option (1-4): ").strip()
                
                if choice == '1':
                    current_ticket = create_ticket_interactive(helpdesk, user_id)
                elif choice == '2':
                    list_user_tickets(helpdesk, user_id)
                elif choice == '3':
                    current_ticket = open_existing_ticket(helpdesk, user_id)
                elif choice == '4':
                    break
                else:
                    print("Invalid option")
            else:
                # In ticket conversation
                print(f"\n🎫 Ticket: {current_ticket.title} ({current_ticket.status.value})")
                print("Type 'back' to return to main menu")
                
                user_input = input("Message: ").strip()
                
                if user_input.lower() == 'back':
                    current_ticket = None
                    continue
                elif not user_input:
                    continue
                
                response = helpdesk.process_ticket_message(
                    current_ticket.id, user_input, user_id
                )
                print(f"AI: {response}")
                
                # Refresh ticket data
                current_ticket = helpdesk.get_ticket(current_ticket.id)
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n👋 Goodbye!")

def create_ticket_interactive(helpdesk, user_id):
    """Create a ticket interactively."""
    print("\n📝 Create New Ticket")
    title = input("Title: ").strip()
    description = input("Description: ").strip()
    priority = input("Priority (low/medium/high/critical) [medium]: ").strip() or "medium"
    
    if title and description:
        ticket = helpdesk.create_ticket(title, description, user_id, priority)
        print(f"✓ Ticket created: {ticket.id[:8]}...")
        return ticket
    else:
        print("❌ Title and description are required")
        return None

def list_user_tickets(helpdesk, user_id):
    """List user's tickets."""
    tickets = helpdesk.list_tickets(user_id=user_id)
    
    if tickets:
        print(f"\n📋 Your Tickets ({len(tickets)}):")
        for i, ticket in enumerate(tickets[:10], 1):  # Show max 10
            print(f"{i}. {ticket.id[:8]}... - {ticket.title} ({ticket.status.value})")
    else:
        print("📭 No tickets found")

def open_existing_ticket(helpdesk, user_id):
    """Open an existing ticket."""
    tickets = helpdesk.list_tickets(user_id=user_id)
    
    if not tickets:
        print("📭 No tickets found")
        return None
    
    print("\n📋 Your Tickets:")
    for i, ticket in enumerate(tickets[:10], 1):
        print(f"{i}. {ticket.id[:8]}... - {ticket.title}")
    
    try:
        choice = int(input("Select ticket number: ")) - 1
        if 0 <= choice < len(tickets):
            return tickets[choice]
        else:
            print("❌ Invalid selection")
            return None
    except ValueError:
        print("❌ Invalid number")
        return None

def knowledge_mode(chatbot):
    """Interactive knowledge management mode."""
    print("📚 Knowledge Mode - Manage knowledge base")
    
    while True:
        try:
            print("\nOptions:")
            print("1. Search knowledge")
            print("2. Add text knowledge")
            print("3. View statistics")
            print("4. Quit")
            
            choice = input("Select option (1-4): ").strip()
            
            if choice == '1':
                query = input("Search query: ").strip()
                if query:
                    results = chatbot.search_knowledge(query, top_k=5)
                    print(f"\n🔍 Found {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        print(f"{i}. Score: {result['score']:.3f}")
                        print(f"   Content: {result['content'][:100]}...")
                        print(f"   Category: {result['metadata'].get('category', 'unknown')}")
            
            elif choice == '2':
                text = input("Knowledge text: ").strip()
                category = input("Category [general]: ").strip() or "general"
                if text:
                    chatbot.add_knowledge_from_text(text, {"category": category})
                    print("✓ Knowledge added")
            
            elif choice == '3':
                stats = chatbot.get_knowledge_stats()
                print(f"\n📊 Knowledge Base Statistics:")
                print(f"Total documents: {stats.get('total_documents', 0)}")
                print(f"Categories: {stats.get('categories', {})}")
                print(f"Index size: {stats.get('index_size', 0)}")
            
            elif choice == '4':
                break
            else:
                print("❌ Invalid option")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()