#!/usr/bin/env python3
"""
Поиск реальных рабочих каналов Telegram
"""
import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

async def find_working_channels():
    """Ищем реальные рабочие каналы"""
    
    # Получаем credentials
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    session_string = os.getenv("TELEGRAM_SESSION")
    
    if not all([api_id, api_hash, session_string]):
        print("❌ Missing Telegram credentials")
        print("Создайте .env файл с:")
        print("TELEGRAM_API_ID=your_api_id")
        print("TELEGRAM_API_HASH=your_api_hash")
        print("TELEGRAM_SESSION=your_session_string")
        return
    
    # Создаем клиент
    client = TelegramClient(
        StringSession(session_string),
        int(api_id),
        api_hash
    )
    
    try:
        await client.start()
        print("✅ Connected to Telegram")
        
        # Список каналов для проверки
        test_channels = [
            # Fashion
            "rogov24",
            "burimovasasha", 
            "zarina_brand",
            "limeofficial",
            "ekonika",
            "sela_brand",
            "lichi",
            "befree_community",
            "mordorblog",
            "bymirraa",
            
            # Beauty
            "goldapple_ru",
            "glamguruu",
            "marietells",
            "sofikshenzdes",
            "writeforfriends",
            
            # Home
            "casacozy",
            "homiesapiens",
            "home_where",
            "objectdesigner"
        ]
        
        working_channels = {
            "fashion": [],
            "beauty": [],
            "home": []
        }
        
        for channel in test_channels:
            try:
                print(f"\n🔍 Testing {channel}...")
                entity = await client.get_entity(channel)
                
                # Получаем информацию о канале
                title = entity.title
                subscribers = getattr(entity, 'participants_count', 'N/A')
                print(f"✅ {channel}: {title} (Subscribers: {subscribers})")
                
                # Проверяем есть ли посты с фото
                photo_posts = []
                async for message in client.iter_messages(entity, limit=20):
                    if message.photo and message.views and message.views >= 1000:
                        photo_posts.append({
                            'id': message.id,
                            'views': message.views,
                            'text': (message.text or "")[:100],
                            'date': message.date
                        })
                        if len(photo_posts) >= 5:  # Достаточно для теста
                            break
                
                print(f"   📸 Found {len(photo_posts)} posts with photos")
                
                if len(photo_posts) >= 3:  # Минимум 3 поста с фото
                    # Определяем категорию
                    if any(word in channel.lower() for word in ['fashion', 'style', 'clothes', 'rogov', 'zarina', 'lime', 'sela', 'lichi', 'befree', 'mordor', 'bymirra']):
                        working_channels["fashion"].append(channel)
                        print(f"   ✅ Added to FASHION category")
                    elif any(word in channel.lower() for word in ['beauty', 'makeup', 'cosmetics', 'goldapple', 'glam', 'marietells', 'sofikshenzdes', 'writeforfriends']):
                        working_channels["beauty"].append(channel)
                        print(f"   ✅ Added to BEAUTY category")
                    elif any(word in channel.lower() for word in ['home', 'interior', 'design', 'casacozy', 'homiesapiens', 'home_where', 'objectdesigner']):
                        working_channels["home"].append(channel)
                        print(f"   ✅ Added to HOME category")
                    else:
                        working_channels["fashion"].append(channel)  # По умолчанию fashion
                        print(f"   ✅ Added to FASHION category (default)")
                else:
                    print(f"   ❌ Not enough photo posts")
                
            except Exception as e:
                print(f"❌ {channel}: {e}")
        
        print(f"\n📊 SUMMARY:")
        print(f"✅ Fashion channels: {len(working_channels['fashion'])}")
        print(f"✅ Beauty channels: {len(working_channels['beauty'])}")
        print(f"✅ Home channels: {len(working_channels['home'])}")
        
        print(f"\n🎯 WORKING CHANNELS:")
        for category, channels in working_channels.items():
            if channels:
                print(f"\n{category.upper()}:")
                for ch in channels:
                    print(f"  - {ch}")
        
        # Сохраняем результат в файл
        with open("working_channels.txt", "w") as f:
            f.write("WORKING TELEGRAM CHANNELS\n")
            f.write("=" * 30 + "\n\n")
            for category, channels in working_channels.items():
                if channels:
                    f.write(f"{category.upper()}:\n")
                    for ch in channels:
                        f.write(f"  - {ch}\n")
                    f.write("\n")
        
        print(f"\n💾 Results saved to working_channels.txt")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(find_working_channels())
