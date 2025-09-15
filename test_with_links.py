#!/usr/bin/env python3
"""
Тест каналов с полными ссылками
"""
import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

async def test_with_links():
    """Тестируем каналы с полными ссылками"""
    
    # Получаем credentials
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    session_string = os.getenv("TELEGRAM_SESSION")
    
    # Создаем клиент
    client = TelegramClient(
        StringSession(session_string),
        int(api_id),
        api_hash
    )
    
    try:
        await client.start()
        print("✅ Connected to Telegram")
        
        # Тестируем с полными ссылками
        test_links = [
            "https://t.me/rogov24",
            "https://t.me/burimovasasha",
            "https://t.me/zarina_brand",
            "https://t.me/goldapple_ru",
            "https://t.me/glamguruu",
            "https://t.me/casacozy",
            "https://t.me/homiesapiens"
        ]
        
        working_channels = []
        
        for link in test_links:
            try:
                print(f"\n🔍 Testing {link}...")
                entity = await client.get_entity(link)
                
                title = entity.title
                subscribers = getattr(entity, 'participants_count', 'N/A')
                print(f"✅ {link}: {title} (Subscribers: {subscribers})")
                
                # Проверяем есть ли посты с фото
                photo_count = 0
                async for message in client.iter_messages(entity, limit=10):
                    if message.photo and message.views and message.views >= 1000:
                        photo_count += 1
                        if photo_count >= 3:
                            break
                
                print(f"   📸 Found {photo_count} posts with photos")
                
                if photo_count >= 1:
                    working_channels.append(link)
                    print(f"   ✅ Added to working channels")
                
            except Exception as e:
                print(f"❌ {link}: {e}")
        
        print(f"\n📊 SUMMARY:")
        print(f"✅ Working channels: {len(working_channels)}")
        
        if working_channels:
            print(f"\n🎯 WORKING CHANNELS:")
            for ch in working_channels:
                print(f"  - {ch}")
        else:
            print(f"\n❌ No working channels found")
            print(f"\n💡 SUGGESTIONS:")
            print(f"1. Проверьте, что каналы существуют")
            print(f"2. Попробуйте другие каналы")
            print(f"3. Убедитесь, что у вас есть доступ к каналам")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_with_links())
