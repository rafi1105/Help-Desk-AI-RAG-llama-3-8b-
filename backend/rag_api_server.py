from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import os
from dotenv import load_dotenv
import json
import time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import datetime
from typing import Dict, List, Any, Optional
import threading
import pickle

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://[::]:3000"])

# Global variables for system
llm = None
search_system = None
feedback_memory = {}
learning_stats = {
    'total_feedback': 0,
    'likes': 0,
    'dislikes': 0,
    'blocked_answers': 0,
    'improved_responses': 0
}

# Load configuration
try:
    import config
    OFFLINE_MODE = getattr(config, 'OFFLINE_MODE', False)
except ImportError:
    # Fallback if config.py doesn't exist
    OFFLINE_MODE = os.getenv('OFFLINE_MODE', 'True').lower() == 'true'

print(f"🔧 Server mode: {'OFFLINE' if OFFLINE_MODE else 'ONLINE'}")

class IntegratedSearchSystem:
    """Integrated system combining JSON analysis with LLaMA model"""

    def __init__(self, data_file_path: str = "enhanced_ndata.json", jsonl_file_path: str = "green_university_30k_instruction_response.jsonl"):
        """Initialize the integrated search system"""

        # NLP setup
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english')) | {"university", "please", "can"}

        # File paths
        self.data_file_path = data_file_path
        self.jsonl_file_path = jsonl_file_path
        self.feedback_file_path = "user_feedback_data.json"
        self.disliked_answers_file = "disliked_answers.json"
        self.blocked_keywords_file = "blocked_keywords.json"
        self.learning_model_file = "learning_model.pkl"

        # Load and process data
        self.load_data()
        self.load_feedback_data()
        self.preprocess_all_data()
        self.train_models()

        print(f"✅ Integrated Search System initialized with {len(self.data)} data points")

    def load_data(self):
        """Load JSON and JSONL data with enhanced processing for learning"""
        self.data = []
        self.instruction_responses = []  # Separate store for instruction-response pairs
        
        # Load enhanced_ndata.json
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            if isinstance(json_data, list):
                for item in json_data:
                    if 'question' in item and 'answer' in item:
                        # Normalize to expected format
                        normalized_item = {
                            'question': item['question'],
                            'answer': item['answer'],
                            'keywords': item.get('keywords', []),
                            'categories': item.get('categories', []),
                            'source': 'enhanced_json',
                            'confidence_score': item.get('confidence_score', 1.0),
                            'question_variations': item.get('question_variations', [])
                        }
                        self.data.append(normalized_item)
        except Exception as e:
            print(f"Error loading JSON data: {e}")
        
        # Load green_university_30k_instruction_response.jsonl with enhanced learning
        try:
            with open(self.jsonl_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f):
                    line = line.strip()
                    if line:
                        item = json.loads(line)
                        if 'instruction' in item and 'output' in item:
                            # Store in instruction_responses for specialized learning
                            instruction_item = {
                                'instruction': item['instruction'],
                                'output': item['output'],
                                'source': 'instruction_dataset',
                                'line_number': line_num
                            }
                            self.instruction_responses.append(instruction_item)
                            
                            # Also convert to general format for unified search
                            normalized_item = {
                                'question': item['instruction'],
                                'answer': item['output'],
                                'keywords': self._extract_keywords_from_text(item['instruction']),
                                'categories': [self._auto_categorize_instruction(item['instruction'])],
                                'source': 'instruction_dataset',
                                'confidence_score': 0.8  # Slightly lower confidence for auto-generated
                            }
                            self.data.append(normalized_item)
        except Exception as e:
            print(f"Error loading JSONL data: {e}")
        
        print(f"Loaded {len(self.data)} total data points from JSON and JSONL files")
        print(f"Loaded {len(self.instruction_responses)} instruction-response pairs for specialized learning")

    def load_feedback_data(self):
        """Load feedback and learning data"""
        # Load disliked answers
        try:
            with open(self.disliked_answers_file, 'r', encoding='utf-8') as f:
                self.disliked_answers = json.load(f)
        except:
            self.disliked_answers = []

        # Load general feedback
        try:
            with open(self.feedback_file_path, 'r', encoding='utf-8') as f:
                self.feedback_data = json.load(f)
        except:
            self.feedback_data = []

        # Load learning model if exists
        try:
            with open(self.learning_model_file, 'rb') as f:
                self.learning_model = pickle.load(f)
        except:
            self.learning_model = None

    def save_feedback_data(self):
        """Save all feedback data"""
        with open(self.disliked_answers_file, "w", encoding='utf-8') as f:
            json.dump(self.disliked_answers, f, indent=2, ensure_ascii=False)

        with open(self.feedback_file_path, "w", encoding='utf-8') as f:
            json.dump(self.feedback_data, f, indent=2, ensure_ascii=False)

        # Save learning model
        if hasattr(self, 'learning_model') and self.learning_model:
            with open(self.learning_model_file, 'wb') as f:
                pickle.dump(self.learning_model, f)

    def preprocess(self, text: str) -> str:
        """Text preprocessing"""
        if not text:
            return ""
        text = text.lower().strip()
        text = ''.join([c for c in text if c.isalnum() or c.isspace()])
        words = [self.lemmatizer.lemmatize(word) for word in text.split()
                if word not in self.stop_words]
        return ' '.join(words)

    def preprocess_all_data(self):
        """Preprocess all data"""
        self.questions = []
        self.answers = []
        self.keywords_list = []
        self.categories = []

        for item in self.data:
            # Skip if answer is blocked
            if any(disliked['answer'] == item['answer'] for disliked in self.disliked_answers):
                continue

            processed_question = self.preprocess(item["question"])
            processed_keywords = [self.preprocess(kw) for kw in item.get("keywords", [])]

            self.questions.append(processed_question)
            self.answers.append(item["answer"])
            self.keywords_list.append(processed_keywords)

            # Determine category
            if "categories" in item and item["categories"]:
                self.categories.append(item["categories"][0])
            else:
                self.categories.append(self._auto_categorize(item.get("keywords", [])))

    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from instruction text for better categorization"""
        if not text:
            return []
        
        # Common university-related keywords
        keywords = []
        text_lower = text.lower()
        
        # Academic keywords
        academic_terms = ['admission', 'fee', 'tuition', 'course', 'program', 'semester', 'gpa', 'grade', 'exam', 'credit']
        for term in academic_terms:
            if term in text_lower:
                keywords.append(term)
        
        # Department keywords
        dept_terms = ['cse', 'computer science', 'engineering', 'bba', 'business', 'english', 'law', 'textile']
        for term in dept_terms:
            if term in text_lower:
                keywords.append(term)
        
        # Facility keywords
        facility_terms = ['library', 'lab', 'hostel', 'cafeteria', 'wifi', 'sports', 'club']
        for term in facility_terms:
            if term in text_lower:
                keywords.append(term)
        
        return list(set(keywords))  # Remove duplicates

    def _auto_categorize_instruction(self, instruction: str) -> str:
        """Auto-categorize instructions for better learning"""
        instruction_lower = instruction.lower()
        
        if any(word in instruction_lower for word in ["fee", "tuition", "cost", "price", "payment"]):
            return "fees_financial"
        elif any(word in instruction_lower for word in ["admission", "requirement", "apply", "enrollment", "deadline"]):
            return "admission_requirements"
        elif any(word in instruction_lower for word in ["program", "course", "department", "cse", "bba", "engineering"]):
            return "academic_programs"
        elif any(word in instruction_lower for word in ["contact", "phone", "email", "address", "location"]):
            return "contact_information"
        elif any(word in instruction_lower for word in ["facility", "library", "lab", "hostel", "cafeteria", "wifi"]):
            return "campus_facilities"
        elif any(word in instruction_lower for word in ["scholarship", "merit", "financial aid"]):
            return "scholarships_aid"
        elif any(word in instruction_lower for word in ["club", "society", "extracurricular", "sports"]):
            return "student_activities"
        else:
            return "general_inquiry"

    def search_instruction_responses(self, user_input: str) -> Dict[str, Any]:
        """Specialized search through instruction-response pairs"""
        if not hasattr(self, 'instruction_responses') or not self.instruction_responses:
            return {"answer": "", "confidence": 0, "method": "no_instruction_data"}
        
        processed_input = self.preprocess(user_input)
        best_match = {"answer": "", "confidence": 0, "instruction": "", "method": "no_match"}
        
        for item in self.instruction_responses:
            processed_instruction = self.preprocess(item['instruction'])
            
            # Calculate similarity
            if processed_instruction and processed_input:
                # Simple word overlap similarity
                input_words = set(processed_input.split())
                instruction_words = set(processed_instruction.split())
                
                if input_words and instruction_words:
                    overlap = len(input_words.intersection(instruction_words))
                    similarity = overlap / max(len(input_words), len(instruction_words))
                    
                    if similarity > best_match["confidence"]:
                        best_match = {
                            "answer": item['output'],
                            "confidence": similarity,
                            "instruction": item['instruction'],
                            "method": "instruction_match"
                        }
        
        return best_match

    def _auto_categorize(self, keywords: List[str]) -> str:
        """Auto-categorize based on keywords"""
        keywords_lower = [kw.lower() for kw in keywords]

        if any(word in keywords_lower for word in ["fee", "tuition", "cost", "price"]):
            return "fees"
        elif any(word in keywords_lower for word in ["admission", "requirement", "apply", "enrollment"]):
            return "admission"
        elif any(word in keywords_lower for word in ["program", "course", "department", "cse", "bba"]):
            return "programs"
        elif any(word in keywords_lower for word in ["contact", "phone", "email", "address"]):
            return "contact"
        else:
            return "general"

    def train_models(self):
        """Train ML models"""
        if not self.questions:
            return

        # TF-IDF Vectorization
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=10000, min_df=1, max_df=0.95)
        self.X = self.vectorizer.fit_transform(self.questions)

        # Category Classification
        if len(set(self.categories)) > 1:
            encoded_categories = LabelEncoder().fit_transform(self.categories)
            X_train, X_test, y_train, y_test = train_test_split(
                self.X, encoded_categories, test_size=0.2, random_state=42
            )
            self.category_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.category_classifier.fit(X_train, y_train)

    def search_json_data(self, user_input: str) -> Dict[str, Any]:
        """Search JSON data for answers"""
        if not self.questions:
            return {"answer": "", "confidence": 0, "method": "no_data"}

        # Check if vectorizer is available
        if not hasattr(self, 'vectorizer') or self.vectorizer is None:
            return {"answer": "", "confidence": 0, "method": "vectorizer_not_trained"}

        processed_input = self.preprocess(user_input)

        # Vectorize input
        try:
            user_vec = self.vectorizer.transform([processed_input])
        except Exception as e:
            print(f"❌ Vectorizer transform error: {e}")
            return {"answer": "", "confidence": 0, "method": "processing_error"}

        # Calculate similarities
        similarities = cosine_similarity(user_vec, self.X).flatten()

        # Find best match
        if len(similarities) > 0:
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]

            if best_score >= 0.25:  # Confidence threshold
                return {
                    "answer": self.answers[best_idx],
                    "confidence": float(best_score),
                    "method": "json_search",
                    "analyzed_items": len(self.questions)
                }

        return {"answer": "", "confidence": 0, "method": "no_match"}

    def generate_llama_response(self, user_input: str, context: str = "") -> str:
        """Generate response using LLaMA model"""
        print(f"🤖 Generating LLaMA response for: '{user_input}'")
        print(f"🤖 LLaMA model available: {llm is not None}")

        if not llm:
            print("❌ LLaMA model not available")
            return "AI model is currently unavailable."

        try:
            # Enhanced prompt for better responses
            if "python" in user_input.lower() or "code" in user_input.lower():
                prompt = f"""You are a helpful programming assistant for Green University students.

Question: {user_input}

Please provide a clear, well-commented Python code solution. Include explanations and best practices.

Answer:"""
                print("🐍 Using Python code prompt")
            elif "calculate" in user_input.lower() or "math" in user_input.lower():
                prompt = f"""You are a helpful assistant specializing in calculations and mathematics.

Question: {user_input}

Please provide a step-by-step solution with clear explanations.

Answer:"""
                print("🔢 Using math calculation prompt")
            else:
                prompt = f"""You are a helpful assistant for Green University of Bangladesh.

Context from knowledge base:
{context}

User Question: {user_input}

Please provide a helpful, accurate answer. If this is about programming or technical topics, include relevant code examples when appropriate.

Answer:"""
                print("🎓 Using general university prompt")

            print(f"📝 Prompt length: {len(prompt)} characters")
            print(f"📝 Prompt preview: {prompt[:200]}...")

            response = llm.invoke(prompt)
            print(f"✅ LLaMA response generated, length: {len(response)}")
            print(f"📄 Response preview: {response[:200]}...")

            return response

        except Exception as e:
            print(f"❌ LLaMA generation error: {e}")
            import traceback
            traceback.print_exc()
            return "I apologize, but I'm having trouble generating a response right now."

    def integrated_search(self, user_input: str) -> Dict[str, Any]:
        """Enhanced integrated search combining JSON data, instruction-responses, and LLaMA model"""
        start_time = time.time()
        print(f"🔍 Starting enhanced integrated search for: '{user_input}'")

        try:
            # First, try specialized instruction-response search
            instruction_result = self.search_instruction_responses(user_input)
            print(f"📚 Instruction search result keys: {list(instruction_result.keys())}")
            print(f"📚 Instruction search result: confidence={instruction_result.get('confidence', 0)}, method={instruction_result.get('method', 'MISSING')}")

            # Then, try general JSON data search
            json_result = self.search_json_data(user_input)
            print(f"📊 JSON search result keys: {list(json_result.keys())}")
            print(f"📊 JSON search result: confidence={json_result.get('confidence', 0)}, method={json_result.get('method', 'MISSING')}")

            # Choose best result from both searches
            best_result = instruction_result if instruction_result.get("confidence", 0) > json_result.get("confidence", 0) else json_result
            print(f"🏆 Best result keys: {list(best_result.keys())}")
            print(f"🏆 Best result confidence: {best_result.get('confidence', 0)}")
            
            if best_result.get("confidence", 0) >= 0.7:  # High confidence from either search
                print("✅ Using high confidence result")
                result = {
                    **best_result,
                    "processing_time": round(time.time() - start_time, 2),
                    "source": f"high_confidence_{best_result.get('method', 'unknown')}"
                }
                return result
            elif best_result.get("confidence", 0) >= 0.25:  # Medium confidence
                if not OFFLINE_MODE and llm:  # Only enhance if online mode and LLaMA available
                    print("🔄 Using medium confidence result, enhancing with LLaMA")
                    
                    # Prepare context from both searches
                    context_parts = []
                    if json_result.get("confidence", 0) > 0.1:
                        context_parts.append(f"JSON Data: {json_result.get('answer', '')}")
                    if instruction_result.get("confidence", 0) > 0.1:
                        context_parts.append(f"Instruction Data: {instruction_result.get('answer', '')}")
                    
                    context = "\n".join(context_parts)
                    enhanced_answer = self.generate_llama_response(user_input, context)

                    return {
                        "answer": enhanced_answer,
                        "confidence": min(best_result.get("confidence", 0) + 0.2, 1.0),
                        "method": "enhanced_multi_source_llama",
                        "analyzed_items": len(self.questions) + len(getattr(self, 'instruction_responses', [])),
                        "processing_time": round(time.time() - start_time, 2),
                        "source": "multi_source_llama_hybrid",
                        "used_sources": ["json_data", "instruction_responses", "llama_enhancement"]
                    }
                else:
                    print("📄 Using medium confidence result (offline mode)")
                    return {
                        **best_result,
                        "processing_time": round(time.time() - start_time, 2),
                        "source": "medium_confidence_offline"
                    }
            else:
                if not OFFLINE_MODE and llm:  # Only use LLaMA if online mode and available
                    print("🤖 Using LLaMA primary response (low confidence from all sources)")
                    # Low confidence from all sources, use LLaMA primarily
                    llama_answer = self.generate_llama_response(user_input)

                    return {
                        "answer": llama_answer,
                        "confidence": 0.8,  # LLaMA responses get high confidence
                        "method": "llama_primary_multi_search",
                        "analyzed_items": len(self.questions) + len(getattr(self, 'instruction_responses', [])),
                        "processing_time": round(time.time() - start_time, 2),
                        "source": "llama_fallback_enhanced"
                    }
                else:
                    print("📝 Using enhanced fallback response (offline mode, low confidence)")
                    # Enhanced offline fallback response
                    return {
                        "answer": "I found some information but I'm not fully confident about the answer. Please rephrase your question or ask about specific topics like admissions, fees, programs, or facilities at Green University.",
                        "confidence": best_result.get("confidence", 0),
                        "method": "enhanced_offline_fallback",
                        "analyzed_items": len(self.questions) + len(getattr(self, 'instruction_responses', [])),
                        "processing_time": round(time.time() - start_time, 2),
                        "source": "fallback_response"
                    }
        except Exception as search_error:
            print(f"❌ Integrated search error: {search_error}")
            import traceback
            traceback.print_exc()
            return {
                "answer": "An error occurred during search. Please try again.",
                "confidence": 0,
                "method": "search_error",
                "analyzed_items": 0,
                "processing_time": round(time.time() - start_time, 2),
                "source": "error_fallback"
            }

    def record_feedback(self, user_question: str, bot_answer: str, feedback_type: str) -> Dict[str, Any]:
        """Record feedback with learning"""
        timestamp = datetime.datetime.now().isoformat()

        # Record feedback
        feedback_entry = {
            'timestamp': timestamp,
            'question': user_question,
            'answer': bot_answer,
            'feedback': feedback_type
        }
        self.feedback_data.append(feedback_entry)

        # Update learning stats
        global learning_stats
        learning_stats['total_feedback'] += 1
        if feedback_type == 'like':
            learning_stats['likes'] += 1
        elif feedback_type == 'dislike':
            learning_stats['dislikes'] += 1
            learning_stats['blocked_answers'] += 1

            # Block the disliked answer
            dislike_entry = {
                'answer': bot_answer,
                'question': user_question,
                'timestamp': timestamp,
                'blocked_permanently': True
            }
            self.disliked_answers.append(dislike_entry)

            # Retrain models without this answer
            self.preprocess_all_data()
            self.train_models()

        # Save feedback data
        self.save_feedback_data()

        return {
            "status": "success",
            "message": f"Feedback recorded: {feedback_type}",
            "learning_stats": learning_stats
        }

def initialize_system():
    """Initialize the integrated system with optional LLaMA and search"""
    global llm, search_system

    if not OFFLINE_MODE:
        # Initialize LLaMA model (online mode)
        try:
            llm = Ollama(model="llama3.2:1b")
            test_response = llm.invoke("Hello")
            print("✅ LLaMA 3.2 model initialized successfully")
            print(f"Test response: {test_response}")
        except Exception as e:
            print(f"❌ Error initializing LLaMA model: {e}")
            print("Make sure Ollama is running and the model is pulled")
            return False
    else:
        print("🔌 OFFLINE MODE: Skipping LLaMA model initialization")
        llm = None

    # Initialize integrated search system (always available)
    try:
        search_system = IntegratedSearchSystem()
        print(f"✅ Search system created: {search_system is not None}")
        print("✅ Integrated search system initialized")
    except Exception as e:
        print(f"❌ Error initializing search system: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests with integrated JSON processing (offline/online)"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing message field',
                'answer': 'Please provide a message to process.',
                'method': 'error',
                'confidence': 0,
                'analyzed_items': 0
            }), 400

        user_message = data['message'].strip()
        if not user_message:
            return jsonify({
                'error': 'Empty message',
                'answer': 'Please enter a valid message.',
                'method': 'error',
                'confidence': 0,
                'analyzed_items': 0
            }), 400

        print(f"📝 Processing message: '{user_message}'")
        print(f"🔍 Search system available: {search_system is not None}")
        print(f"🤖 LLaMA model available: {llm is not None}")
        print(f"🔌 Offline mode: {OFFLINE_MODE}")

        # Use integrated search system
        if search_system:
            try:
                result = search_system.integrated_search(user_message)
                print(f"✅ Search result: method={result.get('method', 'MISSING')}, confidence={result.get('confidence', 0)}")
                print(f"🔍 Full result keys: {list(result.keys())}")

                return jsonify({
                    'answer': result.get('answer', 'No answer generated'),
                    'method': result.get('method', 'unknown_method'),
                    'confidence': result.get('confidence', 0),
                    'analyzed_items': result.get('analyzed_items', 0),
                    'processing_time': result.get('processing_time', 0),
                    'model': 'offline_json' if OFFLINE_MODE else 'integrated_llama3.2_json',
                    'source': result.get('source', 'unknown_source'),
                    'offline_mode': OFFLINE_MODE
                })
            except Exception as search_error:
                print(f"❌ Search system error: {search_error}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'error': f'Search error: {str(search_error)}',
                    'answer': 'An error occurred during search. Please try again.',
                    'method': 'search_error',
                    'confidence': 0,
                    'analyzed_items': 0
                }), 500

        # Fallback if system not initialized
        print("❌ Search system not available")
        return jsonify({
            'answer': 'The AI system is currently initializing. Please try again in a moment.',
            'method': 'system_initializing',
            'confidence': 0,
            'analyzed_items': 0
        })

    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'answer': 'An unexpected error occurred. Please try again.',
            'method': 'error',
            'confidence': 0,
            'analyzed_items': 0
        }), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    """Handle feedback with learning and memory"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        print(f"📝 Feedback received: {data}")

        if search_system:
            result = search_system.record_feedback(
                data.get('question', ''),
                data.get('answer', ''),
                data.get('feedback', 'unknown')
            )

            return jsonify({
                'status': 'success',
                'message': 'Feedback recorded and learning updated',
                'learning_stats': result['learning_stats'],
                'blocked_answers': len(search_system.disliked_answers),
                'total_feedback': len(search_system.feedback_data)
            })

        return jsonify({
            'status': 'success',
            'message': 'Feedback recorded (system learning temporarily disabled)',
            'blocked_answers': 0,
            'total_feedback': 0
        })

    except Exception as e:
        print(f"❌ Feedback endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    mode_status = "OFFLINE MODE" if OFFLINE_MODE else "ONLINE MODE"
    return jsonify({
        'message': f'Green University Integrated RAG API Server ({mode_status})',
        'status': 'running',
        'mode': 'offline' if OFFLINE_MODE else 'online',
        'endpoints': {
            'GET /health': 'Health check',
            'GET /stats': 'System statistics',
            'POST /chat': 'Chat with AI',
            'POST /feedback': 'Submit feedback with learning'
        },
        'features': [
            'JSON data analysis' + (' (Offline Only)' if OFFLINE_MODE else ' with LLaMA enhancement'),
            'Reinforcement learning from feedback',
            'Memory and continuous learning',
            'No internet connection required' if OFFLINE_MODE else 'Requires Ollama for LLaMA'
        ]
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'mode': 'offline' if OFFLINE_MODE else 'online',
        'llm_loaded': llm is not None,
        'search_system_loaded': search_system is not None,
        'model': 'offline_json_search' if OFFLINE_MODE else 'llama3.2:1b + integrated_search',
        'timestamp': time.time(),
        'learning_active': True,
        'offline_capable': True
    })

@app.route('/stats', methods=['GET'])
def stats():
    """Get system statistics"""
    global learning_stats

    if search_system:
        return jsonify({
            'total_feedback': learning_stats['total_feedback'],
            'likes': learning_stats['likes'],
            'dislikes': learning_stats['dislikes'],
            'blocked_answers': learning_stats['blocked_answers'],
            'improved_responses': learning_stats['improved_responses'],
            'available_data': len(search_system.questions) if hasattr(search_system, 'questions') else 0,
            'total_original_data': len(search_system.data) if hasattr(search_system, 'data') else 0,
            'llm_active': llm is not None,
            'learning_enabled': True
        })

    return jsonify({
        'total_feedback': learning_stats['total_feedback'],
        'likes': learning_stats['likes'],
        'dislikes': learning_stats['dislikes'],
        'blocked_answers': learning_stats['blocked_answers'],
        'available_data': 0,
        'total_original_data': 0,
        'llm_active': llm is not None,
        'learning_enabled': False
    })

if __name__ == '__main__':
    mode_text = "OFFLINE" if OFFLINE_MODE else "Integrated LLaMA 3.2 + JSON"
    print(f"🚀 Initializing {mode_text} RAG API Server...")
    try:
        if initialize_system():
            print("✅ System initialized successfully")
            print("🌐 Starting Flask server on port 5000...")
            features_text = "JSON analysis + Offline processing" if OFFLINE_MODE else "JSON analysis + LLaMA enhancement + RL learning"
            print(f"🎯 Features: {features_text}")
            if OFFLINE_MODE:
                print("🔌 OFFLINE MODE: No internet connection required")
            else:
                print("🌐 ONLINE MODE: Requires Ollama for LLaMA functionality")
            app.run(host='0.0.0.0', port=5000, debug=False)
        else:
            print("❌ Failed to initialize system")
            if not OFFLINE_MODE:
                print("💡 Make sure Ollama is running with: ollama serve")
                print("💡 And the model is pulled with: ollama pull llama3.2:1b")
            else:
                print("💡 Check that ndata.json file exists and is valid")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
