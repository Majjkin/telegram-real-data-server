#!/usr/bin/env python3
"""
Тест стороннего API с токеном
"""
import requests
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_third_party_apis():
    """Тестируем различные сторонние API"""
    
    token = "2i92Ks59Z5ILIhG5BLDmRS0nWAXGacsSreHvRnKEnS5rHTe6qdcksAnjnGA4Eek6ZQvHNYLL9CBUI"
    
    # Список возможных API endpoints
    api_endpoints = [
        "https://api.telegram.org/bot{token}/getMe",
        "https://api.telegram.org/bot{token}/getUpdates", 
        "https://api.telegram.org/bot{token}/getChat",
        "https://api.telegram.org/bot{token}/getUpdates",
        "https://api.telegram.org/bot{token}/sendMessage",
        "https://api.telegram.org/bot{token}/getWebhookInfo"
    ]
    
    print(f"🔍 Testing token with different endpoints...")
    
    for endpoint in api_endpoints:
        try:
            url = endpoint.format(token=token)
            print(f"\n🔍 Testing: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"   ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Тест с разными параметрами
    print(f"\n🔍 Testing with different parameters...")
    
    test_params = [
        {"chat_id": "@rogov24"},
        {"chat_id": "rogov24"},
        {"chat_id": "https://t.me/rogov24"},
        {"chat_id": "t.me/rogov24"},
        {"username": "rogov24"},
        {"channel": "rogov24"}
    ]
    
    for params in test_params:
        try:
            url = f"https://api.telegram.org/bot{token}/getChat"
            print(f"\n🔍 Testing getChat with params: {params}")
            
            response = requests.get(url, params=params, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"   ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_third_party_apis()
