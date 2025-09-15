#!/usr/bin/env python3
"""
Детальный тест канала @rogov24
"""
import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

async def test_rogov24():
    """Детальный тест канала @rogov24"""
    
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
        
        # Тестируем разные варианты имени канала
        test_variants = [
            "rogov24",
            "@rogov24", 
            "https://t.me/rogov24",
            "t.me/rogov24"
        ]
        
        for variant in test_variants:
            try:
                print(f"\n🔍 Testing variant: '{variant}'")
                entity = await client.get_entity(variant)
                
                title = entity.title
                subscribers = getattr(entity, 'participants_count', 'N/A')
                username = getattr(entity, 'username', 'N/A')
                print(f"✅ SUCCESS! {variant}")
                print(f"   Title: {title}")
                print(f"   Username: {username}")
                print(f"   Subscribers: {subscribers}")
                
                # Проверяем есть ли посты
                print(f"\n📄 Checking posts...")
                post_count = 0
                photo_posts = 0
                
                async for message in client.iter_messages(entity, limit=20):
                    post_count += 1
                    if message.photo:
                        photo_posts += 1
                        print(f"   📸 Post {message.id}: {message.views} views, photo: {message.photo}")
                    else:
                        print(f"   📝 Post {message.id}: {message.views} views, text: {(message.text or '')[:50]}...")
                    
                    if post_count >= 10:  # Ограничиваем для теста
                        break
                
                print(f"\n📊 Summary:")
                print(f"   Total posts checked: {post_count}")
                print(f"   Posts with photos: {photo_posts}")
                
                if photo_posts >= 3:
                    print(f"   ✅ Channel has enough photo posts!")
                    return True
                else:
                    print(f"   ❌ Not enough photo posts")
                
            except Exception as e:
                print(f"❌ {variant}: {e}")
        
        print(f"\n❌ None of the variants worked")
        return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_rogov24())
