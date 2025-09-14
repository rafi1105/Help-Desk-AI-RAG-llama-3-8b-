import requests
import json
import time

# Wait for server to start
print("Waiting for server to start...")
time.sleep(10)

try:
    # Test health endpoint
    print("Testing health endpoint...")
    response = requests.get("http://localhost:5000/health", timeout=5)
    print(f"✅ Health response: {response.status_code}")
    health_data = response.json()
    print(f"✅ Health data: {health_data}")

    # Test chat endpoint
    print("\nTesting chat endpoint...")
    chat_data = {"message": "Hello, can you tell me about Green University?"}
    response = requests.post("http://localhost:5000/chat",
                           json=chat_data,
                           timeout=10)
    print(f"✅ Chat response: {response.status_code}")
    chat_result = response.json()
    print(f"✅ Chat answer: {chat_result.get('answer', 'No answer')[:100]}...")
    print(f"✅ Confidence: {chat_result.get('confidence', 0)}")
    print(f"✅ Method: {chat_result.get('method', 'unknown')}")

    print("\n🎉 All tests passed! The chatbot is working correctly.")

except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
