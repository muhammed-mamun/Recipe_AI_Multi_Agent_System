#!/usr/bin/env python3
"""
Test OpenRouter API connection
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
import requests

# Load environment
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(backend_dir, '.env'))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")

print("=" * 80)
print("🔧 OPENROUTER API CONNECTION TEST")
print("=" * 80)
print(f"\nAPI Key: {OPENROUTER_API_KEY[:20]}..." if OPENROUTER_API_KEY else "❌ No API Key found")
print(f"Model: {OPENROUTER_MODEL}")
print()

if not OPENROUTER_API_KEY:
    print("❌ ERROR: OPENROUTER_API_KEY not found in .env file")
    sys.exit(1)

# Test API connection
print("Testing API connection...")
try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "user", "content": "Say 'Hello World' and nothing else."}
            ]
        },
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if 'choices' in data and len(data['choices']) > 0:
            message = data['choices'][0]['message']['content']
            print(f"✅ SUCCESS! Response: {message}")
        else:
            print(f"⚠️ Unexpected response format: {data}")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

print("\n" + "=" * 80)
