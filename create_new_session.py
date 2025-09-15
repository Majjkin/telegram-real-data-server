#!/usr/bin/env python3
"""
Создание новой Telegram сессии
"""
import os
from telethon.sync import TelegramClient
from dotenv import load_dotenv

load_dotenv()

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

if not api_id or not api_hash:
    print("❌ TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env file")
    exit(1)

print(f"📱 API ID: {api_id}")
print(f"📱 API Hash: {api_hash}")

# Используем уникальное имя сессии
session_name = "telegram_session_new_v2"

try:
    client = TelegramClient(session_name, int(api_id), api_hash)
    print("🔌 Connecting to Telegram...")
    client.connect()

    if not client.is_user_authorized():
        print("🔐 User not authorized. Starting authorization...")
        client.start(
            phone=lambda: input('📞 Please enter your phone number (e.g., +1234567890): '),
            code_callback=lambda: input('🔑 Please enter the code you received: ')
        )
        print("✅ Authorization successful!")
    else:
        print("✅ Already authorized.")

    # Получаем строку сессии
    session_string = client.session.save()
    print(f"\n🎉 SUCCESS! Your new TELEGRAM_SESSION string:")
    print(f"TELEGRAM_SESSION={session_string}")
    print(f"\n📋 Copy this string and add it to Railway environment variables.")
    
    # Сохраняем в файл
    with open("new_session_string.txt", "w") as f:
        f.write(session_string)
    print(f"💾 Session string saved to new_session_string.txt")

except Exception as e:
    print(f"❌ An error occurred: {e}")
finally:
    if client.is_connected():
        client.disconnect()
        print("🔌 Disconnected from Telegram.")
