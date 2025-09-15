#!/usr/bin/env python3
"""
Проверка документации Telemetr API
"""
import requests
import json

def check_telemetr_docs():
    """Проверяем документацию Telemetr API"""
    
    # Проверяем доступность API
    base_url = "https://api.telemetr.me"
    
    try:
        # Проверяем базовый endpoint
        print("🔍 Checking Telemetr API availability...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        # Проверяем документацию
        print(f"\n🔍 Checking API documentation...")
        doc_urls = [
            f"{base_url}/docs",
            f"{base_url}/api-docs",
            f"{base_url}/swagger",
            f"{base_url}/openapi.json",
            f"{base_url}/v1",
            f"{base_url}/api/v1"
        ]
        
        for url in doc_urls:
            try:
                response = requests.get(url, timeout=5)
                print(f"   {url}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ Found documentation at {url}")
            except:
                print(f"   ❌ {url}: Error")
        
        # Проверяем разные версии API
        print(f"\n🔍 Checking different API versions...")
        versions = ["v1", "v2", "1.0", "1.3.0"]
        
        for version in versions:
            try:
                url = f"{base_url}/{version}"
                response = requests.get(url, timeout=5)
                print(f"   {version}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ Found API version {version}")
            except:
                print(f"   ❌ {version}: Error")
        
        # Проверяем конкретные endpoints
        print(f"\n🔍 Checking specific endpoints...")
        endpoints = [
            "/channels",
            "/publications", 
            "/stats",
            "/search",
            "/api/channels",
            "/api/publications"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                response = requests.get(url, timeout=5)
                print(f"   {endpoint}: {response.status_code}")
                if response.status_code != 404:
                    print(f"   Response: {response.text[:100]}...")
            except:
                print(f"   ❌ {endpoint}: Error")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_telemetr_docs()
