#!/usr/bin/env python3
"""
Отладка сессии Telegram
"""
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

if not api_id or not api_hash:
    print("❌ TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env file")
    exit(1)

try:
    # Создаем клиент с StringSession
    session = StringSession()
    client = TelegramClient(session, int(api_id), api_hash)
    
    print("Connecting to Telegram...")
    client.connect()

    if not client.is_user_authorized():
        print("User not authorized. Sending authorization request...")
        client.start(phone=lambda: input('Please enter your phone number (e.g., +1234567890): '),
                     code_callback=lambda: input('Please enter the code you received: '))
        print("Authorization successful!")
    else:
        print("Already authorized.")

    # Получаем session string
    session_string = session.save()
    print(f"\nSession type: {type(session)}")
    print(f"Session string: {session_string}")
    print(f"Session string length: {len(session_string) if session_string else 'None'}")
    
    if session_string:
        print(f"\nYour TELEGRAM_SESSION string:")
        print(f"TELEGRAM_SESSION={session_string}")
        
        # Сохраняем в файл
        with open("session_string.txt", "w") as f:
            f.write(session_string)
        print(f"Session string saved to session_string.txt")
    else:
        print(f"❌ Session string is None!")

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
finally:
    if client.is_connected():
        client.disconnect()
        print("Disconnected from Telegram.")
