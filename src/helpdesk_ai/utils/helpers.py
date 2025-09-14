"""
Utility functions for Help Desk AI system.
"""
import json
import os
from typing import Dict, List, Any
import logging

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('helpdesk_ai.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_sample_knowledge_base() -> List[Dict[str, Any]]:
    """Load sample knowledge base data."""
    sample_data = [
        {
            "question": "How do I reset my password?",
            "answer": "To reset your password: 1) Go to the login page, 2) Click 'Forgot Password', 3) Enter your email address, 4) Check your email for reset instructions, 5) Follow the link and create a new password.",
            "category": "account_management",
            "tags": ["password", "reset", "login", "account"]
        },
        {
            "question": "How do I update my profile information?",
            "answer": "To update your profile: 1) Log into your account, 2) Go to Settings or Profile, 3) Click Edit Profile, 4) Update the required fields, 5) Save your changes.",
            "category": "account_management",
            "tags": ["profile", "update", "settings", "personal_info"]
        },
        {
            "question": "What are your support hours?",
            "answer": "Our support team is available Monday through Friday, 9:00 AM to 6:00 PM EST. For urgent issues outside these hours, please use our emergency contact form.",
            "category": "support_info",
            "tags": ["hours", "schedule", "availability", "contact"]
        },
        {
            "question": "How do I cancel my subscription?",
            "answer": "To cancel your subscription: 1) Log into your account, 2) Go to Billing or Subscription settings, 3) Click Cancel Subscription, 4) Follow the confirmation steps. Note: Cancellation takes effect at the end of your current billing period.",
            "category": "billing",
            "tags": ["cancel", "subscription", "billing", "account"]
        },
        {
            "question": "How do I download my data?",
            "answer": "To download your data: 1) Go to Settings, 2) Click Data & Privacy, 3) Select Download My Data, 4) Choose the data types you want, 5) Click Request Download. You'll receive an email when your data is ready.",
            "category": "data_privacy",
            "tags": ["download", "data", "export", "privacy"]
        },
        {
            "question": "Why is my account locked?",
            "answer": "Accounts are typically locked due to: 1) Multiple failed login attempts, 2) Suspicious activity detected, 3) Security policy violations. To unlock: 1) Wait 30 minutes and try again, 2) Use password reset, 3) Contact support if the issue persists.",
            "category": "security",
            "tags": ["locked", "account", "security", "login"]
        },
        {
            "question": "How do I enable two-factor authentication?",
            "answer": "To enable 2FA: 1) Go to Security Settings, 2) Click Two-Factor Authentication, 3) Choose your method (SMS or authenticator app), 4) Follow the setup instructions, 5) Save your backup codes in a safe place.",
            "category": "security",
            "tags": ["2fa", "security", "authentication", "setup"]
        },
        {
            "question": "How do I report a bug or technical issue?",
            "answer": "To report a bug: 1) Go to Help Center, 2) Click Report a Bug, 3) Describe the issue in detail, 4) Include steps to reproduce, 5) Attach screenshots if helpful, 6) Submit the report. Our team will investigate and respond within 24-48 hours.",
            "category": "technical_support",
            "tags": ["bug", "report", "technical", "issue"]
        },
        {
            "question": "How do I change my email address?",
            "answer": "To change your email: 1) Go to Account Settings, 2) Click Email Preferences, 3) Enter your new email address, 4) Verify the new email through the confirmation link, 5) Your email will be updated once verified.",
            "category": "account_management",
            "tags": ["email", "change", "update", "account"]
        },
        {
            "question": "What payment methods do you accept?",
            "answer": "We accept the following payment methods: 1) Credit cards (Visa, MasterCard, American Express), 2) PayPal, 3) Bank transfers (for enterprise accounts), 4) Digital wallets (Apple Pay, Google Pay). All payments are processed securely.",
            "category": "billing",
            "tags": ["payment", "methods", "billing", "credit_card"]
        }
    ]
    
    return sample_data

def create_sample_tickets() -> List[Dict[str, Any]]:
    """Create sample ticket data."""
    sample_tickets = [
        {
            "title": "Cannot access my account",
            "description": "I'm unable to log into my account. I keep getting an 'invalid credentials' error even though I'm sure my password is correct.",
            "user_id": "user123",
            "priority": "high",
            "category": "account_access"
        },
        {
            "title": "Payment failed",
            "description": "My monthly payment failed and I received an error message. My credit card should be valid. Please help resolve this.",
            "user_id": "user456",
            "priority": "medium",
            "category": "billing"
        },
        {
            "title": "Feature request: Dark mode",
            "description": "It would be great to have a dark mode option for the interface. Many users would appreciate this feature for better user experience.",
            "user_id": "user789",
            "priority": "low",
            "category": "feature_request"
        },
        {
            "title": "Data export not working",
            "description": "I requested a data export three days ago but haven't received the download link yet. The status still shows 'processing'.",
            "user_id": "user101",
            "priority": "medium",
            "category": "data_export"
        },
        {
            "title": "Security alert received",
            "description": "I received a security alert about a login from an unfamiliar location. I want to make sure my account is secure.",
            "user_id": "user202",
            "priority": "high",
            "category": "security"
        }
    ]
    
    return sample_tickets

def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate JSON structure has required fields."""
    return all(field in data for field in required_fields)

def sanitize_text(text: str) -> str:
    """Sanitize text input for processing."""
    # Remove potential harmful characters
    sanitized = text.replace('<script>', '').replace('</script>', '')
    sanitized = sanitized.replace('<', '&lt;').replace('>', '&gt;')
    return sanitized.strip()

def format_response(response: str) -> str:
    """Format chatbot response for better readability."""
    # Add proper spacing and formatting
    formatted = response.strip()
    
    # Add proper punctuation if missing
    if formatted and not formatted.endswith(('.', '!', '?')):
        formatted += '.'
    
    return formatted

def export_data_to_json(data: Any, filename: str) -> str:
    """Export data to JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        return f"Data exported successfully to {filename}"
    except Exception as e:
        return f"Error exporting data: {str(e)}"

def load_data_from_json(filename: str) -> Any:
    """Load data from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {filename}: {e}")
        return None

def ensure_directory_exists(directory: str) -> None:
    """Ensure directory exists, create if it doesn't."""
    os.makedirs(directory, exist_ok=True)

def get_file_size(filename: str) -> str:
    """Get human-readable file size."""
    try:
        size = os.path.getsize(filename)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except OSError:
        return "Unknown"