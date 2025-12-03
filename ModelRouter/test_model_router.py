import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def test_chat():
    print("Testing Chat Endpoint...")
    
    # 1. First Query (Should hit LLM)
    query = "Write a python function to calculate fibonacci"
    print(f"\nSending Query 1: '{query}'")
    start = time.time()
    res = requests.post(f"{BASE_URL}/api/chat", json={"text": query})
    print(f"Status: {res.status_code}")
    data = res.json()
    print(f"Response Source: {data.get('source')}")
    print(f"Model: {data.get('model')}")
    print(f"Time: {time.time() - start:.2f}s")
    
    assert "LLM" in data.get("source")
    assert "coding" in data.get("categories")

    # 2. Second Query (Should hit Memory Cache)
    print(f"\nSending Query 2 (Same as 1): '{query}'")
    start = time.time()
    res = requests.post(f"{BASE_URL}/api/chat", json={"text": query})
    data = res.json()
    print(f"Response Source: {data.get('source')}")
    print(f"Time: {time.time() - start:.2f}s")
    
    assert "Memory Cache" in data.get("source")

    # 3. Different Query (Should hit different LLM)
    query2 = "Tell me a creative story about a robot"
    print(f"\nSending Query 3: '{query2}'")
    res = requests.post(f"{BASE_URL}/api/chat", json={"text": query2})
    data = res.json()
    print(f"Response Source: {data.get('source')}")
    print(f"Model: {data.get('model')}")
    
    assert "LLM" in data.get("source")
    assert "creative" in data.get("categories")

def test_knowledge():
    print("\nTesting Knowledge Endpoint...")
    text = "The secret code for the vault is 12345."
    res = requests.post(f"{BASE_URL}/api/knowledge", json={"text": text})
    print(f"Add Knowledge Status: {res.status_code}")
    assert res.status_code == 200

    # Query asking about the secret
    query = "What is the secret code?"
    print(f"Asking about secret: '{query}'")
    res = requests.post(f"{BASE_URL}/api/chat", json={"text": query})
    data = res.json()
    print(f"Response: {data.get('text')}")
    # Note: Mock LLM might not actually use the context intelligently, but we can check if it received it
    # In our MockLLM implementation: response_text += f"\nContext used: {context[:50]}..."
    assert "The secret code" in data.get("text")

if __name__ == "__main__":
    # Wait for server to start if running in parallel (manual step usually)
    # For this script, we assume server is running.
    try:
        test_chat()
        test_knowledge()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTests Failed: {e}")
