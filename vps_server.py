#!/usr/bin/env python3
"""
Стабильный сервер для VPS с реальными данными из Telegram
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import io
import time
import requests
import logging
import os
import asyncio
from datetime import datetime, timedelta
import random

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Модели данных
class FeedItem(BaseModel):
    id: str
    channel: str
    message_id: int
    text: str
    views: int
    likes: int
    comments: int
    date: str
    media_url: str
    post_url: str

class PromptReq(BaseModel):
    feed_item_id: str

# Реальные рабочие каналы
WORKING_CHANNELS = {
    "fashion": ["rogov24", "burimovasasha", "zarina_brand"]
}

# Telegram клиент с кэшированием
class TelegramClient:
    def __init__(self):
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.session_string = os.getenv("TELEGRAM_SESSION")
        self.client = None
        self.connected = False
        self.connection_lock = asyncio.Lock()
        self.cache = {}  # Кэш для постов
        self.cache_timeout = 300  # 5 минут
        
    async def connect(self):
        """Подключение к Telegram"""
        async with self.connection_lock:
            if self.connected:
                return True
                
            if not all([self.api_id, self.api_hash, self.session_string]):
                logger.warning("❌ Telegram credentials not found - using demo mode")
                return False
                
            try:
                from telethon import TelegramClient as TGClient
                from telethon.sessions import StringSession
                
                logger.info("🔌 Creating Telegram client...")
                self.client = TGClient(
                    StringSession(self.session_string),
                    int(self.api_id),
                    self.api_hash
                )
                
                logger.info("🔌 Starting Telegram client...")
                await self.client.start()
                self.connected = True
                logger.info("✅ Telegram client connected successfully!")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to connect to Telegram: {e}")
                logger.error(f"❌ Error type: {type(e).__name__}")
                logger.error(f"❌ Error details: {str(e)}")
                self.connected = False
                return False
    
    async def get_channel_posts(self, channel_username: str, limit: int = 10):
        """Получение реальных постов из канала с кэшированием"""
        # Проверяем кэш
        cache_key = f"{channel_username}_{limit}"
        if cache_key in self.cache:
            cache_time, posts = self.cache[cache_key]
            if time.time() - cache_time < self.cache_timeout:
                logger.info(f"📦 Using cached posts for {channel_username}")
                return posts
        
        logger.info(f"🔍 Fetching real posts from {channel_username}")
        
        # Подключаемся если еще не подключены
        logger.info(f"🔌 Attempting to connect to Telegram...")
        if not await self.connect():
            logger.warning(f"📱 Telegram not connected, using demo for {channel_username}")
            return self._get_demo_posts(channel_username, limit)
        
        try:
            logger.info(f"🔍 Fetching real posts from {channel_username}")
            posts = []
            
            # Получаем entity канала
            try:
                entity = await self.client.get_entity(channel_username)
                logger.info(f"✅ Found channel: {entity.title}")
            except Exception as e:
                logger.error(f"❌ Channel {channel_username} not found: {e}")
                return self._get_demo_posts(channel_username, limit)
            
            # Получаем сообщения
            message_count = 0
            async for message in self.client.iter_messages(entity, limit=limit*5):
                if message.views and message.views >= 500:  # Минимум 500 просмотров
                    post_data = {
                        'id': f"{channel_username}_{message.id}",
                        'channel': channel_username,
                        'message_id': message.id,
                        'text': (message.text or "No text")[:200],
                        'views': message.views or 0,
                        'likes': getattr(message.reactions, 'count', 0) if message.reactions else 0,
                        'comments': message.replies.replies if message.replies else 0,
                        'date': message.date.isoformat(),
                        'media_url': f"/photo/{channel_username}/{message.id}" if message.photo else "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=600&fit=crop",
                        'post_url': f"https://t.me/{channel_username}/{message.id}"
                    }
                    posts.append(post_data)
                    message_count += 1
                    logger.info(f"📄 Found post {message.id} with {message.views} views")
                    
                    if message_count >= limit:
                        break
            
            logger.info(f"✅ Retrieved {len(posts)} real posts from {channel_username}")
            
            # Сохраняем в кэш
            self.cache[cache_key] = (time.time(), posts)
            logger.info(f"📦 Cached {len(posts)} posts for {channel_username}")
            
            return posts
            
        except Exception as e:
            logger.error(f"❌ Error getting posts from {channel_username}: {e}")
            return self._get_demo_posts(channel_username, limit)
    
    def _get_demo_posts(self, channel_username: str, limit: int):
        """Демо данные для канала"""
        demo_posts = []
        for i in range(limit):
            post_id = f"{channel_username}_demo_{i+1}"
            demo_posts.append({
                'id': post_id,
                'channel': channel_username,
                'message_id': i+1,
                'text': f"Demo post from {channel_username} #{i+1} - testing interface",
                'views': 15000 + i * 1000,
                'likes': 750 + i * 50,
                'comments': 150 + i * 10,
                'date': '2024-01-15T10:00:00Z',
                'media_url': f"https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=600&fit=crop",
                'post_url': f"https://t.me/{channel_username}/{i+1}"
            })
        return demo_posts

# Создаем приложение
app = FastAPI(title="Creative MVP - VPS Server", version="1.0.0")

# Telegram клиент
telegram_client = TelegramClient()

@app.get("/")
async def root():
    return {"message": "Creative MVP - VPS Server", "status": "running"}

@app.get("/telegram/channels/{category}")
async def get_channel_posts(category: str, limit: int = 6):
    """Получение постов из каналов по категории"""
    try:
        if category not in WORKING_CHANNELS:
            raise HTTPException(404, f"Category {category} not found")
        
        all_posts = []
        for channel in WORKING_CHANNELS[category]:
            posts = await telegram_client.get_channel_posts(channel, limit)
            all_posts.extend(posts)
        
        # Сортируем по дате (новые сначала)
        all_posts.sort(key=lambda x: x['date'], reverse=True)
        
        return {
            "category": category,
            "posts": all_posts[:limit],
            "total": len(all_posts)
        }
    except Exception as e:
        logger.error(f"❌ Error getting posts: {e}")
        raise HTTPException(500, f"Error getting posts: {str(e)}")

@app.get("/photo/{channel}/{message_id}")
async def get_photo(channel: str, message_id: int):
    """Получение фото из Telegram через прокси"""
    try:
        # Подключаемся к Telegram если еще не подключены
        await telegram_client.connect()
        
        if not telegram_client.client:
            raise HTTPException(500, "Telegram client not connected")
        
        # Получаем канал
        entity = await telegram_client.client.get_entity(channel)
        
        # Получаем сообщение
        message = await telegram_client.client.get_messages(entity, ids=message_id)
        if not message or not message.photo:
            raise HTTPException(404, "Photo not found")
        
        # Скачиваем фото в память
        photo_bytes = await telegram_client.client.download_media(message.photo, file=bytes)
        
        if not photo_bytes:
            raise HTTPException(404, "Photo download failed")
        
        # Возвращаем фото как поток
        return StreamingResponse(
            io.BytesIO(photo_bytes),
            media_type="image/jpeg",
            headers={"Cache-Control": "public, max-age=3600"}
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting photo: {e}")
        raise HTTPException(500, f"Error getting photo: {str(e)}")

@app.post("/prompts/generate")
async def gen_prompts(req: PromptReq):
    """Генерация промптов для поста"""
    logger.info(f"🎨 Generating prompts for: {req.feed_item_id}")
    
    return {
        "prompts": [
            f"Create a stunning fashion image inspired by {req.feed_item_id}",
            f"Generate beautiful content based on {req.feed_item_id}",
            f"Design an elegant concept for {req.feed_item_id}"
        ],
        "seed": random.randint(1000, 9999),
        "provider": "telegram_real"
    }

@app.post("/creative/generate")
async def creative_generate(req: PromptReq):
    """Генерация изображений"""
    logger.info(f"🎨 Generating image for: {req.feed_item_id}")
    
    # Проверяем FAL_KEY
    fal_key = os.getenv("FAL_KEY")
    logger.info(f"🔍 FAL_KEY check: {fal_key is not None}")
    if fal_key:
        logger.info(f"🔑 FAL_KEY found: {fal_key[:20]}...")
    else:
        logger.warning("❌ FAL_KEY not found, using demo image")
        return {
            "image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=600&fit=crop",
            "prompt": f"Generated image for {req.feed_item_id}",
            "seed": random.randint(1000, 9999),
            "provider": "demo"
        }
    
    # Используем FAL API для реальной генерации
    try:
        import fal_client
        
        logger.info(f"🔑 FAL_KEY found: {fal_key[:20]}...")
        
        # Генерируем изображение через FAL
        logger.info(f"🎨 Submitting to FAL API...")
        result = fal_client.submit(
            "fal-ai/flux-pro",
            arguments={
                "prompt": f"Fashion image inspired by {req.feed_item_id}, high quality, professional photography",
                "image_size": "square_hd",
                "num_inference_steps": 28
            }
        )
        
        logger.info(f"⏳ Waiting for FAL API result...")
        # Получаем результат
        result = fal_client.wait(result)
        image_url = result["images"][0]["url"]
        prompt = f"Generated image for {req.feed_item_id}"
        
        logger.info(f"✅ Generated image for {req.feed_item_id}: {image_url}")
        return {
            "image_url": image_url,
            "prompt": prompt,
            "seed": random.randint(1000, 9999),
            "provider": "fal_ai"
        }
        
    except Exception as e:
        logger.error(f"❌ FAL API error: {e}")
        # Fallback на демо изображение
        return {
            "image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=600&fit=crop",
            "prompt": f"Generated image for {req.feed_item_id}",
            "seed": random.randint(1000, 9999),
            "provider": "demo_fallback"
        }

@app.get("/ui", response_class=HTMLResponse)
def ui():
    """Главная страница с UI"""
    return """<!doctype html>
<html>
<head>
    <title>Creative MVP - VPS Server</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .tabs { display: flex; justify-content: center; margin-bottom: 20px; }
        .tab { padding: 10px 20px; margin: 0 5px; background: #007bff; color: white; border: none; cursor: pointer; border-radius: 5px; }
        .tab.active { background: #0056b3; }
        .tab:hover { background: #0056b3; }
        .feed { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .post { background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .post img { width: 100%; height: 300px; object-fit: cover; }
        .post-content { padding: 15px; }
        .post-stats { display: flex; justify-content: space-between; margin-top: 10px; color: #666; }
        .btn { background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #218838; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #5a6268; }
        .loading { text-align: center; padding: 20px; color: #666; }
        .status { background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Creative MVP - VPS Server</h1>
            <p>Real posts from Telegram channels with beautiful images</p>
        </div>
        
        <div class="status">
            ✅ Connected to VPS Server - Loading real data
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="loadFeed('fashion')">Fashion</button>
        </div>
        
        <div id="feed" class="feed">
            <div class="loading">Loading real posts from Telegram...</div>
        </div>
    </div>

    <script>
        async function loadFeed(category) {
            // Показываем загрузку
            document.getElementById('feed').innerHTML = '<div class="loading">Loading real posts from Telegram...</div>';
            
            try {
                const response = await fetch(`/telegram/channels/${category}?limit=6`);
                const data = await response.json();
                
                if (data.posts) {
                    displayPosts(data.posts);
                } else {
                    document.getElementById('feed').innerHTML = '<div class="loading">No posts found</div>';
                }
            } catch (error) {
                console.error('Error loading feed:', error);
                document.getElementById('feed').innerHTML = '<div class="loading">Error loading posts</div>';
            }
        }
        
        function displayPosts(posts) {
            const feed = document.getElementById('feed');
            feed.innerHTML = posts.map(post => `
                <div class="post">
                    <img src="${post.media_url}" alt="Post image" onerror="this.src='https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=600&fit=crop'">
                    <div class="post-content">
                        <h3>${post.text}</h3>
                        <div class="post-stats">
                            <span>👁️ ${post.views.toLocaleString()}</span>
                            <span>❤️ ${post.likes}</span>
                            <span>💬 ${post.comments}</span>
                        </div>
                        <button class="btn" onclick="generatePrompts('${post.id}')">Промпт</button>
                        <button class="btn btn-secondary" onclick="generateImage('${post.id}')">Сгенерировать</button>
                    </div>
                </div>
            `).join('');
        }
        
        async function generatePrompts(feedItemId) {
            try {
                const response = await fetch('/prompts/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ feed_item_id: feedItemId })
                });
                const data = await response.json();
                alert('Generated prompts:\\n' + data.prompts.join('\\n'));
            } catch (error) {
                console.error('Error generating prompts:', error);
                alert('Error generating prompts');
            }
        }
        
        async function generateImage(feedItemId) {
            try {
                const response = await fetch('/creative/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ feed_item_id: feedItemId })
                });
                const data = await response.json();
                alert('Generated image: ' + data.image_url);
            } catch (error) {
                console.error('Error generating image:', error);
                alert('Error generating image');
            }
        }
        
        // Загружаем посты при загрузке страницы
        loadFeed('fashion');
    </script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
