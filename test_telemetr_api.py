#!/usr/bin/env python3
"""
Тест Telemetr API для получения данных каналов
"""
import requests
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_telemetr_api():
    """Тестируем Telemetr API"""
    
    # Ваш токен от Telemetr
    token = "2i92Ks59Z5ILIhG5BLDmRS0nWAXGacsSreHvRnKEnS5rHTe6qdcksAnjnGA4Eek6ZQvHNYLL9CBUI"
    
    # Базовый URL для Telemetr API
    base_url = "https://api.telemetr.me"
    
    # Заголовки с авторизацией
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Тест 1: Получаем информацию о каналах
        print("🔍 Testing channels endpoint...")
        response = requests.get(f"{base_url}/channels", headers=headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            channels = response.json()
            print(f"✅ Channels retrieved successfully!")
            print(f"Response: {json.dumps(channels, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"❌ Channels failed: {response.text}")
        
        # Тест 2: Ищем конкретные каналы
        print(f"\n🔍 Testing channel search...")
        
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
                print(f"\n🔍 Searching for: {channel}")
                
                # Пробуем найти канал
                response = requests.get(f"{base_url}/channels", 
                                      headers=headers,
                                      params={"search": channel})
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ SUCCESS!")
                    print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}...")
                    
                    # Проверяем есть ли результаты
                    if 'data' in data and len(data['data']) > 0:
                        working_channels.append(channel)
                        print(f"   ✅ Found {len(data['data'])} results for {channel}")
                    else:
                        print(f"   ❌ No results for {channel}")
                else:
                    print(f"   ❌ Failed: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Тест 3: Получаем публикации канала
        if working_channels:
            print(f"\n🔍 Testing channel publications...")
            test_channel = working_channels[0]
            
            try:
                response = requests.get(f"{base_url}/channels/{test_channel}/publications", 
                                      headers=headers)
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    publications = response.json()
                    print(f"✅ Publications retrieved for {test_channel}!")
                    print(f"Response: {json.dumps(publications, indent=2, ensure_ascii=False)[:500]}...")
                else:
                    print(f"❌ Publications failed: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error getting publications: {e}")
        
        print(f"\n📊 SUMMARY:")
        print(f"✅ Working channels: {len(working_channels)}")
        
        if working_channels:
            print(f"\n🎯 WORKING CHANNELS:")
            for ch in working_channels:
                print(f"  - {ch}")
        else:
            print(f"\n❌ No working channels found")
            print(f"\n💡 POSSIBLE SOLUTIONS:")
            print(f"1. Проверьте правильность токена")
            print(f"2. Убедитесь, что токен активен")
            print(f"3. Проверьте права доступа")
        
        return len(working_channels) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_telemetr_api()
