from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Load data
try:
    with open('enhanced_ndata.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} questions")
except Exception as e:
    print(f"Error loading data: {e}")
    data = []

@app.route('/chat', methods=['POST'])
def chat():
    try:
        request_data = request.get_json()
        user_message = request_data.get('message', '').lower()
        
        # Simple keyword search
        for item in data:
            if any(keyword.lower() in user_message for keyword in item.get('keywords', [])):
                return jsonify({'answer': item['answer']})
        
        # Default response
        return jsonify({'answer': 'I can help you with questions about Green University. Please ask about admissions, fees, programs, or facilities.'})
        
    except Exception as e:
        return jsonify({'answer': f'Error: {str(e)}'})

@app.route('/', methods=['GET'])
def root():
    return jsonify({'message': 'Simple Green University Chatbot API', 'status': 'running'})

if __name__ == '__main__':
    print("Starting simple server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
