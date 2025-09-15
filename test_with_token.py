#!/usr/bin/env python3
"""
Тест подключения через сторонний токен
"""
import requests
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_telegram_api_with_token():
    """Тестируем Telegram API с токеном"""
    
    # Ваш токен
    token = "2i92Ks59Z5ILIhG5BLDmRS0nWAXGacsSreHvRnKEnS5rHTe6qdcksAnjnGA4Eek6ZQvHNYLL9CBUI"
    
    # Базовый URL для Telegram API
    base_url = f"https://api.telegram.org/bot{token}"
    
    try:
        # Тест 1: Получаем информацию о боте
        print("🔍 Testing bot info...")
        response = requests.get(f"{base_url}/getMe")
        
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Bot connected successfully!")
            print(f"   Bot name: {bot_info['result']['first_name']}")
            print(f"   Username: @{bot_info['result']['username']}")
            print(f"   ID: {bot_info['result']['id']}")
        else:
            print(f"❌ Bot API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Тест 2: Пробуем получить обновления
        print(f"\n🔍 Testing updates...")
        response = requests.get(f"{base_url}/getUpdates")
        
        if response.status_code == 200:
            updates = response.json()
            print(f"✅ Updates retrieved: {len(updates['result'])} updates")
        else:
            print(f"❌ Updates failed: {response.status_code}")
        
        # Тест 3: Пробуем найти каналы через Bot API
        print(f"\n🔍 Testing channel search...")
        
        # Список каналов для тестирования
        test_channels = [
            "rogov24",
            "burimovasasha", 
            "zarina_brand",
            "goldapple_ru",
            "glamguruu"
        ]
        
        working_channels = []
        
        for channel in test_channels:
            try:
                # Пробуем получить информацию о канале
                response = requests.get(f"{base_url}/getChat", params={"chat_id": f"@{channel}"})
                
                if response.status_code == 200:
                    chat_info = response.json()
                    if chat_info['ok']:
                        print(f"✅ {channel}: {chat_info['result']['title']}")
                        working_channels.append(channel)
                    else:
                        print(f"❌ {channel}: {chat_info['description']}")
                else:
                    print(f"❌ {channel}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {channel}: {e}")
        
        print(f"\n📊 SUMMARY:")
        print(f"✅ Working channels: {len(working_channels)}")
        
        if working_channels:
            print(f"\n🎯 WORKING CHANNELS:")
            for ch in working_channels:
                print(f"  - {ch}")
        else:
            print(f"\n❌ No working channels found")
            print(f"\n💡 POSSIBLE SOLUTIONS:")
            print(f"1. Токен может быть только для Bot API")
            print(f"2. Нужны дополнительные права для доступа к каналам")
            print(f"3. Попробуем другой подход")
        
        return len(working_channels) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_telegram_api_with_token()
