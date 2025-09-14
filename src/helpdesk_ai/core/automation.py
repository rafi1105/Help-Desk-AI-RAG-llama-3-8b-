"""
Help Desk automation system for ticket handling and learning.
"""
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import os

class TicketStatus(Enum):
    """Ticket status enumeration."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(Enum):
    """Ticket priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Ticket:
    """Help desk ticket."""
    
    def __init__(self, title: str, description: str, user_id: str, 
                 priority: TicketPriority = TicketPriority.MEDIUM):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.user_id = user_id
        self.priority = priority
        self.status = TicketStatus.OPEN
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.messages = []
        self.tags = []
        self.assigned_to = None
        self.resolution = None
    
    def add_message(self, content: str, sender: str, sender_type: str = "user"):
        """Add message to ticket."""
        message = {
            "id": str(uuid.uuid4()),
            "content": content,
            "sender": sender,
            "sender_type": sender_type,  # user, agent, system
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def update_status(self, status: TicketStatus):
        """Update ticket status."""
        self.status = status
        self.updated_at = datetime.now()
    
    def set_resolution(self, resolution: str):
        """Set ticket resolution."""
        self.resolution = resolution
        self.status = TicketStatus.RESOLVED
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ticket to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": self.messages,
            "tags": self.tags,
            "assigned_to": self.assigned_to,
            "resolution": self.resolution
        }

class HelpDeskAutomation:
    """Help desk automation system."""
    
    def __init__(self, chatbot, data_dir: str = "./data"):
        self.chatbot = chatbot
        self.data_dir = data_dir
        self.tickets = {}
        self.knowledge_learning = []
        
        # Create data directory
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing tickets
        self.load_tickets()
    
    def create_ticket(self, title: str, description: str, user_id: str, 
                     priority: str = "medium") -> Ticket:
        """Create a new help desk ticket."""
        try:
            priority_enum = TicketPriority(priority.lower())
        except ValueError:
            priority_enum = TicketPriority.MEDIUM
        
        ticket = Ticket(title, description, user_id, priority_enum)
        self.tickets[ticket.id] = ticket
        
        # Auto-generate initial response
        initial_response = self.generate_initial_response(ticket)
        ticket.add_message(initial_response, "helpdesk_ai", "system")
        
        # Save tickets
        self.save_tickets()
        
        return ticket
    
    def process_ticket_message(self, ticket_id: str, message: str, user_id: str) -> str:
        """Process a message for a ticket and generate response."""
        if ticket_id not in self.tickets:
            return "Ticket not found."
        
        ticket = self.tickets[ticket_id]
        
        # Add user message
        ticket.add_message(message, user_id, "user")
        
        # Generate context from ticket history
        context = self.build_ticket_context(ticket)
        
        # Generate response using chatbot
        response = self.chatbot.chat(f"Ticket: {ticket.title}\nUser message: {message}\nContext: {context}")
        
        # Add response to ticket
        ticket.add_message(response, "helpdesk_ai", "agent")
        
        # Check if ticket should be auto-resolved
        self.check_auto_resolution(ticket, message, response)
        
        # Learn from interaction
        self.learn_from_interaction(ticket, message, response)
        
        # Save tickets
        self.save_tickets()
        
        return response
    
    def generate_initial_response(self, ticket: Ticket) -> str:
        """Generate initial automated response for a new ticket."""
        prompt = f"""
        A new help desk ticket has been created:
        Title: {ticket.title}
        Description: {ticket.description}
        Priority: {ticket.priority.value}
        
        Generate a professional initial response acknowledging the ticket and providing helpful guidance.
        """
        
        response = self.chatbot.chat(prompt)
        return response
    
    def build_ticket_context(self, ticket: Ticket) -> str:
        """Build context from ticket history."""
        context_parts = [
            f"Ticket ID: {ticket.id}",
            f"Title: {ticket.title}",
            f"Description: {ticket.description}",
            f"Status: {ticket.status.value}",
            f"Priority: {ticket.priority.value}"
        ]
        
        # Add recent messages
        if ticket.messages:
            context_parts.append("Recent messages:")
            for msg in ticket.messages[-5:]:  # Last 5 messages
                sender_type = msg.get("sender_type", "unknown")
                content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                context_parts.append(f"{sender_type}: {content}")
        
        return "\n".join(context_parts)
    
    def check_auto_resolution(self, ticket: Ticket, user_message: str, bot_response: str):
        """Check if ticket should be automatically resolved."""
        resolution_keywords = [
            "thank you", "thanks", "resolved", "fixed", "working now", 
            "problem solved", "issue fixed", "that worked"
        ]
        
        user_message_lower = user_message.lower()
        if any(keyword in user_message_lower for keyword in resolution_keywords):
            ticket.set_resolution(f"Auto-resolved based on user confirmation: {user_message}")
    
    def learn_from_interaction(self, ticket: Ticket, user_message: str, bot_response: str):
        """Learn from ticket interactions to improve knowledge base."""
        learning_data = {
            "ticket_id": ticket.id,
            "ticket_title": ticket.title,
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp": datetime.now().isoformat(),
            "priority": ticket.priority.value,
            "status": ticket.status.value
        }
        
        self.knowledge_learning.append(learning_data)
        
        # Add to knowledge base if it seems like a good Q&A pair
        if len(user_message) > 10 and len(bot_response) > 20:
            knowledge_text = f"Question: {user_message}\nAnswer: {bot_response}"
            self.chatbot.add_knowledge_from_text(
                knowledge_text, 
                {"category": "learned_interactions", "ticket_id": ticket.id}
            )
    
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ID."""
        return self.tickets.get(ticket_id)
    
    def list_tickets(self, status: Optional[str] = None, user_id: Optional[str] = None) -> List[Ticket]:
        """List tickets with optional filters."""
        tickets = list(self.tickets.values())
        
        if status:
            tickets = [t for t in tickets if t.status.value == status]
        
        if user_id:
            tickets = [t for t in tickets if t.user_id == user_id]
        
        # Sort by creation date (newest first)
        tickets.sort(key=lambda t: t.created_at, reverse=True)
        
        return tickets
    
    def get_ticket_statistics(self) -> Dict[str, Any]:
        """Get help desk statistics."""
        total_tickets = len(self.tickets)
        
        if total_tickets == 0:
            return {"total_tickets": 0}
        
        status_counts = {}
        priority_counts = {}
        
        for ticket in self.tickets.values():
            status = ticket.status.value
            priority = ticket.priority.value
            
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "total_tickets": total_tickets,
            "status_distribution": status_counts,
            "priority_distribution": priority_counts,
            "learning_interactions": len(self.knowledge_learning)
        }
    
    def save_tickets(self):
        """Save tickets to JSON file."""
        try:
            tickets_data = {
                ticket_id: ticket.to_dict() 
                for ticket_id, ticket in self.tickets.items()
            }
            
            with open(os.path.join(self.data_dir, "tickets.json"), "w") as f:
                json.dump(tickets_data, f, indent=2, default=str)
            
            # Save learning data
            with open(os.path.join(self.data_dir, "learning_data.json"), "w") as f:
                json.dump(self.knowledge_learning, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving tickets: {e}")
    
    def load_tickets(self):
        """Load tickets from JSON file."""
        try:
            tickets_file = os.path.join(self.data_dir, "tickets.json")
            if os.path.exists(tickets_file):
                with open(tickets_file, "r") as f:
                    tickets_data = json.load(f)
                
                for ticket_id, ticket_data in tickets_data.items():
                    ticket = Ticket(
                        ticket_data["title"],
                        ticket_data["description"],
                        ticket_data["user_id"],
                        TicketPriority(ticket_data["priority"])
                    )
                    ticket.id = ticket_data["id"]
                    ticket.status = TicketStatus(ticket_data["status"])
                    ticket.created_at = datetime.fromisoformat(ticket_data["created_at"])
                    ticket.updated_at = datetime.fromisoformat(ticket_data["updated_at"])
                    ticket.messages = ticket_data.get("messages", [])
                    ticket.tags = ticket_data.get("tags", [])
                    ticket.assigned_to = ticket_data.get("assigned_to")
                    ticket.resolution = ticket_data.get("resolution")
                    
                    self.tickets[ticket_id] = ticket
            
            # Load learning data
            learning_file = os.path.join(self.data_dir, "learning_data.json")
            if os.path.exists(learning_file):
                with open(learning_file, "r") as f:
                    self.knowledge_learning = json.load(f)
                    
        except Exception as e:
            print(f"Error loading tickets: {e}")
    
    def export_knowledge_base(self) -> Dict[str, Any]:
        """Export learned knowledge for backup or analysis."""
        return {
            "tickets_count": len(self.tickets),
            "learning_interactions": self.knowledge_learning,
            "knowledge_stats": self.chatbot.get_knowledge_stats(),
            "export_timestamp": datetime.now().isoformat()
        }