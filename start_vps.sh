#!/bin/bash
# Скрипт запуска сервера на VPS

echo "🚀 Starting Creative MVP Server on VPS..."

# Устанавливаем зависимости
echo "📦 Installing dependencies..."
pip3 install -r vps_requirements.txt

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
TELEGRAM_API_ID=20858291
TELEGRAM_API_HASH=a5db966aa915a7497d5bec95b0a3ae58
TELEGRAM_SESSION=your_session_string_here
FAL_KEY=c4d53f4d-5c0f-43be-a053-4ddf7c9a4290:9d63bf23a83054c728b9b14d077370f0
EOF
    echo "⚠️  Please update TELEGRAM_SESSION in .env file!"
fi

# Запускаем сервер
echo "🎯 Starting server on port 8000..."
python3 vps_server.py
