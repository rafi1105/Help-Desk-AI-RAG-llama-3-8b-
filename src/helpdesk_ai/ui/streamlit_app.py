"""
Streamlit web interface for Help Desk AI Chat-Bot.
"""
import streamlit as st
import json
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from helpdesk_ai.models.chatbot import HelpDeskChatBot
from helpdesk_ai.core.automation import HelpDeskAutomation, TicketPriority

# Page configuration
st.set_page_config(
    page_title="Help Desk AI Chat-Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "chatbot" not in st.session_state:
    with st.spinner("Initializing AI models... This may take a few minutes."):
        st.session_state.chatbot = HelpDeskChatBot()
        st.session_state.helpdesk = HelpDeskAutomation(st.session_state.chatbot)

if "current_ticket_id" not in st.session_state:
    st.session_state.current_ticket_id = None

if "user_id" not in st.session_state:
    st.session_state.user_id = "user_" + datetime.now().strftime("%Y%m%d_%H%M%S")

def main():
    """Main application."""
    st.title("🤖 Help Desk AI Chat-Bot")
    st.markdown("*AI-powered help desk with RAG and knowledge base learning*")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Chat Interface", "Ticket Management", "Knowledge Base", "Settings"]
        )
        
        st.divider()
        
        # User info
        st.subheader("User Info")
        st.session_state.user_id = st.text_input(
            "User ID", 
            value=st.session_state.user_id
        )
        
        # Quick stats
        st.subheader("Quick Stats")
        stats = st.session_state.helpdesk.get_ticket_statistics()
        st.metric("Total Tickets", stats.get("total_tickets", 0))
        
        kb_stats = st.session_state.chatbot.get_knowledge_stats()
        st.metric("Knowledge Documents", kb_stats.get("total_documents", 0))
    
    # Main content based on page selection
    if page == "Chat Interface":
        chat_interface()
    elif page == "Ticket Management":
        ticket_management()
    elif page == "Knowledge Base":
        knowledge_base_page()
    elif page == "Settings":
        settings_page()

def chat_interface():
    """Chat interface page."""
    st.header("💬 Chat with AI Assistant")
    
    # Ticket selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        tickets = st.session_state.helpdesk.list_tickets(user_id=st.session_state.user_id)
        ticket_options = ["New Conversation"] + [f"{t.id[:8]}... - {t.title}" for t in tickets]
        
        selected_ticket = st.selectbox(
            "Select or create conversation:",
            ticket_options
        )
        
        if selected_ticket != "New Conversation":
            ticket_id = selected_ticket.split(" - ")[0].replace("...", "")
            # Find full ticket ID
            for t in tickets:
                if t.id.startswith(ticket_id):
                    st.session_state.current_ticket_id = t.id
                    break
    
    with col2:
        if st.button("New Ticket", type="primary"):
            st.session_state.current_ticket_id = None
    
    # Display current conversation
    if st.session_state.current_ticket_id:
        ticket = st.session_state.helpdesk.get_ticket(st.session_state.current_ticket_id)
        if ticket:
            st.subheader(f"Ticket: {ticket.title}")
            st.caption(f"Status: {ticket.status.value} | Priority: {ticket.priority.value}")
            
            # Display messages
            for message in ticket.messages:
                sender_type = message.get("sender_type", "user")
                content = message["content"]
                sender = message["sender"]
                
                if sender_type == "user":
                    st.chat_message("user").write(content)
                else:
                    st.chat_message("assistant").write(content)
            
            # Message input for existing ticket
            user_message = st.chat_input("Type your message...")
            if user_message:
                st.chat_message("user").write(user_message)
                
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = st.session_state.helpdesk.process_ticket_message(
                            st.session_state.current_ticket_id,
                            user_message,
                            st.session_state.user_id
                        )
                    st.write(response)
                
                st.rerun()
    
    else:
        # New ticket creation
        st.subheader("Create New Ticket")
        
        with st.form("new_ticket_form"):
            title = st.text_input("Ticket Title", placeholder="Brief description of your issue")
            description = st.text_area("Description", placeholder="Detailed description of your issue")
            priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
            
            submitted = st.form_submit_button("Create Ticket")
            
            if submitted and title and description:
                # Create new ticket
                ticket = st.session_state.helpdesk.create_ticket(
                    title, description, st.session_state.user_id, priority
                )
                st.session_state.current_ticket_id = ticket.id
                st.success(f"Ticket created: {ticket.id}")
                st.rerun()
        
        # Direct chat without ticket
        st.divider()
        st.subheader("Quick Chat (No Ticket)")
        
        # Display chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        for exchange in st.session_state.chat_history:
            st.chat_message("user").write(exchange["user"])
            st.chat_message("assistant").write(exchange["assistant"])
        
        # Quick chat input
        quick_message = st.chat_input("Ask a quick question...")
        if quick_message:
            st.chat_message("user").write(quick_message)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot.chat(quick_message)
                st.write(response)
            
            st.session_state.chat_history.append({
                "user": quick_message,
                "assistant": response
            })
            st.rerun()

def ticket_management():
    """Ticket management page."""
    st.header("🎫 Ticket Management")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "open", "in_progress", "resolved", "closed"]
        )
    
    with col2:
        user_filter = st.selectbox(
            "Filter by User",
            ["All Users", st.session_state.user_id]
        )
    
    with col3:
        if st.button("Refresh"):
            st.rerun()
    
    # Get filtered tickets
    status = None if status_filter == "All" else status_filter
    user_id = None if user_filter == "All Users" else user_filter
    
    tickets = st.session_state.helpdesk.list_tickets(status=status, user_id=user_id)
    
    # Display tickets
    if tickets:
        for ticket in tickets:
            with st.expander(f"🎫 {ticket.title} ({ticket.status.value})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Description:** {ticket.description}")
                    st.write(f"**User:** {ticket.user_id}")
                    st.write(f"**Created:** {ticket.created_at.strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Updated:** {ticket.updated_at.strftime('%Y-%m-%d %H:%M')}")
                    
                    if ticket.resolution:
                        st.success(f"**Resolution:** {ticket.resolution}")
                
                with col2:
                    st.write(f"**ID:** {ticket.id[:8]}...")
                    st.write(f"**Priority:** {ticket.priority.value}")
                    st.write(f"**Messages:** {len(ticket.messages)}")
                    
                    if st.button(f"Open Chat", key=f"open_{ticket.id}"):
                        st.session_state.current_ticket_id = ticket.id
                        st.switch_page("pages/chat.py") if "pages/chat.py" in st.session_state else None
    else:
        st.info("No tickets found matching the current filters.")
    
    # Ticket statistics
    st.divider()
    st.subheader("📊 Statistics")
    
    stats = st.session_state.helpdesk.get_ticket_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tickets", stats.get("total_tickets", 0))
    
    with col2:
        open_tickets = stats.get("status_distribution", {}).get("open", 0)
        st.metric("Open Tickets", open_tickets)
    
    with col3:
        resolved_tickets = stats.get("status_distribution", {}).get("resolved", 0)
        st.metric("Resolved Tickets", resolved_tickets)
    
    with col4:
        learning_count = stats.get("learning_interactions", 0)
        st.metric("Learning Interactions", learning_count)

def knowledge_base_page():
    """Knowledge base management page."""
    st.header("📚 Knowledge Base Management")
    
    # Knowledge base stats
    kb_stats = st.session_state.chatbot.get_knowledge_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Documents", kb_stats.get("total_documents", 0))
    
    with col2:
        st.metric("Categories", len(kb_stats.get("categories", {})))
    
    with col3:
        st.metric("Vector Index Size", kb_stats.get("index_size", 0))
    
    # Add knowledge
    st.subheader("📝 Add Knowledge")
    
    tab1, tab2, tab3 = st.tabs(["JSON Data", "Text Document", "File Upload"])
    
    with tab1:
        st.write("Add structured JSON data to the knowledge base:")
        
        json_input = st.text_area(
            "JSON Data",
            placeholder='{"question": "How to reset password?", "answer": "Click on forgot password link..."}'
        )
        
        category = st.text_input("Category", value="help_desk")
        
        if st.button("Add JSON Data"):
            try:
                json_data = json.loads(json_input)
                st.session_state.chatbot.add_knowledge_from_json(json_data, category)
                st.success("JSON data added to knowledge base!")
            except json.JSONDecodeError:
                st.error("Invalid JSON format")
    
    with tab2:
        st.write("Add text document to the knowledge base:")
        
        text_input = st.text_area("Text Content", placeholder="Enter your knowledge content...")
        text_category = st.text_input("Category", value="general", key="text_category")
        
        if st.button("Add Text Document"):
            if text_input.strip():
                st.session_state.chatbot.add_knowledge_from_text(
                    text_input, 
                    {"category": text_category}
                )
                st.success("Text document added to knowledge base!")
            else:
                st.error("Please enter some text content")
    
    with tab3:
        st.write("Upload JSON file to knowledge base:")
        
        uploaded_file = st.file_uploader("Choose JSON file", type=["json"])
        file_category = st.text_input("Category", value="uploaded", key="file_category")
        
        if uploaded_file and st.button("Upload File"):
            try:
                json_data = json.load(uploaded_file)
                st.session_state.chatbot.knowledge_base.load_json_file(
                    uploaded_file.name, 
                    file_category
                )
                st.success("File uploaded to knowledge base!")
            except Exception as e:
                st.error(f"Error uploading file: {e}")
    
    # Search knowledge base
    st.divider()
    st.subheader("🔍 Search Knowledge Base")
    
    search_query = st.text_input("Search Query", placeholder="Enter your search terms...")
    
    if search_query:
        results = st.session_state.chatbot.search_knowledge(search_query)
        
        if results:
            for i, result in enumerate(results, 1):
                with st.expander(f"Result {i} (Score: {result['score']:.3f})"):
                    st.write(result["content"])
                    st.json(result["metadata"])
        else:
            st.info("No results found.")

def settings_page():
    """Settings and configuration page."""
    st.header("⚙️ Settings")
    
    # Model settings
    st.subheader("Model Configuration")
    
    st.info("Current model settings are loaded from environment variables and config files.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Current Settings:**")
        st.write(f"- Model: {st.session_state.chatbot.tokenizer.name_or_path if st.session_state.chatbot.tokenizer else 'Not loaded'}")
        st.write(f"- Device: {'CUDA' if st.session_state.chatbot.model and next(st.session_state.chatbot.model.parameters()).is_cuda else 'CPU'}")
    
    with col2:
        st.write("**Knowledge Base:**")
        kb_stats = st.session_state.chatbot.get_knowledge_stats()
        st.write(f"- Documents: {kb_stats.get('total_documents', 0)}")
        st.write(f"- Categories: {len(kb_stats.get('categories', {}))}")
    
    # Data management
    st.divider()
    st.subheader("Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Save Knowledge Base"):
            st.session_state.chatbot.knowledge_base.save_knowledge_base()
            st.success("Knowledge base saved!")
    
    with col2:
        if st.button("Clear Chat History"):
            st.session_state.chatbot.clear_conversation_history()
            if "chat_history" in st.session_state:
                st.session_state.chat_history = []
            st.success("Chat history cleared!")
    
    with col3:
        if st.button("Export Data"):
            export_data = st.session_state.helpdesk.export_knowledge_base()
            st.download_button(
                "Download Export",
                json.dumps(export_data, indent=2, default=str),
                file_name=f"helpdesk_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # System info
    st.divider()
    st.subheader("System Information")
    
    import torch
    import transformers
    
    st.write("**Environment:**")
    st.write(f"- Python: {sys.version}")
    st.write(f"- PyTorch: {torch.__version__}")
    st.write(f"- Transformers: {transformers.__version__}")
    st.write(f"- CUDA Available: {torch.cuda.is_available()}")

if __name__ == "__main__":
    main()