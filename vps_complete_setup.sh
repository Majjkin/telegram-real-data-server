#!/bin/bash

echo "🚀 Complete VPS Setup for Creative MVP..."

# Go to project directory
cd /opt/creative-mvp

# Create .env file
echo "📝 Creating .env file..."
cat > .env << 'EOF'
TELEGRAM_API_ID=28008814
TELEGRAM_API_HASH=34d4bdb7e7195a76a4fa339f1a6570d7
TELEGRAM_SESSION=1ApWapzMBu0efa-JyN2Q9IoxiExEKTHWQ_7NsSoK5EE9wwYZsyLi50npUhlbYdaQPj8X-vSNX_abjdLbydsCAu4erZ13HPpSSr0qHpd8aAohDd63Ji5iw3aSZjIRTPXme4ytDMuJWiNOq_afABWZwPHN5AHezb3g31VDBFwHciinLtOKnoVYv6yZgyM2wZoUGnptWfnydCg0Dw17d4jWOMIcgaqm1HZ24snWSdBaHE-Hgmks8NayA19Vn0NHoyJvivsKvNqnqKAczBTenLRPyX0JKtRFSkPzWYFBSD08DT49y90KIOCHNV4gvMIdW0qQGBdji--RRqjV0fAUgYo6631qREyDLMa=
FAL_KEY=c4d53f4d-5c0f-43be-a053-4ddf7c9a4290:9d63bf23a83054c728b9b14d077370f0
DEMO_MODE=0
EOF

# Create vps_server.py
echo "📝 Creating vps_server.py..."
cat > vps_server.py << 'EOF'
import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import io
import time
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Creative MVP Server")

# Telegram configuration
API_ID = 28008814
API_HASH = "34d4bdb7e7195a76a4fa339f1a6570d7"
SESSION_STRING = "1ApWapzMBu0efa-JyN2Q9IoxiExEKTHWQ_7NsSoK5EE9wwYZsyLi50npUhlbYdaQPj8X-vSNX_abjdLbydsCAu4erZ13HPpSSr0qHpd8aAohDd63Ji5iw3aSZjIRTPXme4ytDMuJWiNOq_afABWZwPHN5AHezb3g31VDBFwHciinLtOKnoVYv6yZgyM2wZoUGnptWfnydCg0Dw17d4jWOMIcgaqm1HZ24snWSdBaHE-Hgmks8NayA19Vn0NHoyJvivsKvNqnqKAczBTenLRPyX0JKtRFSkPzWYFBSD08DT49y90KIOCHNV4gvMIdW0qQGBdji--RRqjV0fAUgYo6631qREyDLMa="

# Working channels for MVP
WORKING_CHANNELS = {
    "fashion": [
        "rogov24",
        "burimovasasha", 
        "zarina_brand"
    ]
}

class FeedItem(BaseModel):
    id: str
    channel: str
    text: str
    media_url: Optional[str] = None
    views: int
    date: str

class TelegramClientWrapper:
    def __init__(self):
        self.client = None
        self.connection_attempted = False
        self.cache = {}
        self.cache_timeout = 300
        
    async def connect(self):
        if self.connection_attempted:
            return self.client is not None
            
        if not API_ID or not API_HASH or not SESSION_STRING:
            logger.warning("Missing Telegram credentials")
            return False
            
        try:
            self.client = TelegramClient('session', API_ID, API_HASH)
            await self.client.start()
            self.connection_attempted = True
            logger.info("Connected to Telegram successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            self.connection_attempted = True
            return False
    
    async def get_channel_posts(self, category: str, limit: int = 6) -> List[FeedItem]:
        # Check cache first
        cache_key = f"{category}_{limit}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                logger.info(f"Returning cached data for {category}")
                return cached_data
        
        if not await self.connect():
            logger.warning("Telegram not connected, returning demo data")
            return self._get_demo_data(category, limit)
        
        try:
            posts = []
            channels = WORKING_CHANNELS.get(category, [])
            
            for channel_username in channels:
                try:
                    # Get channel entity
                    channel = await self.client.get_entity(channel_username)
                    
                    # Get messages
                    message_count = 0
                    async for message in self.client.iter_messages(channel, limit=limit*5):
                        if message_count >= limit:
                            break
                            
                        if message.views and message.views >= 500:
                            # Check if message has photo
                            media_url = None
                            if message.media and isinstance(message.media, MessageMediaPhoto):
                                media_url = f"/photo/{channel_username}/{message.id}"
                            
                            post = FeedItem(
                                id=f"{channel_username}_{message.id}",
                                channel=channel_username,
                                text=message.text or "No text",
                                media_url=media_url,
                                views=message.views or 0,
                                date=message.date.strftime("%Y-%m-%d %H:%M")
                            )
                            posts.append(post)
                            message_count += 1
                            
                except Exception as e:
                    logger.error(f"Error fetching from {channel_username}: {e}")
                    continue
            
            # Cache the results
            self.cache[cache_key] = (posts, time.time())
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching posts: {e}")
            return self._get_demo_data(category, limit)
    
    def _get_demo_data(self, category: str, limit: int) -> List[FeedItem]:
        demo_posts = [
            FeedItem(
                id="demo_1",
                channel="rogov24",
                text="Стильный образ для осени 🍂",
                media_url="/photo/rogov24/1",
                views=1500,
                date="2024-01-15 14:30"
            ),
            FeedItem(
                id="demo_2", 
                channel="burimovasasha",
                text="Новая коллекция уже в продаже! ✨",
                media_url="/photo/burimovasasha/2",
                views=2300,
                date="2024-01-15 13:45"
            ),
            FeedItem(
                id="demo_3",
                channel="zarina_brand",
                text="Как сочетать цвета в одежде 🎨",
                media_url="/photo/zarina_brand/3",
                views=1800,
                date="2024-01-15 12:20"
            )
        ]
        return demo_posts[:limit]

# Initialize Telegram client
telegram_client = TelegramClientWrapper()

@app.get("/")
async def root():
    return {"message": "Creative MVP Server is running!"}

@app.get("/api/feed/{category}")
async def get_feed(category: str, limit: int = 6):
    try:
        posts = await telegram_client.get_channel_posts(category, limit)
        return {"posts": posts}
    except Exception as e:
        logger.error(f"Error getting feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/photo/{channel}/{message_id}")
async def get_photo(channel: str, message_id: str):
    try:
        if not await telegram_client.connect():
            # Return demo image if Telegram not connected
            demo_url = f"https://picsum.photos/400/600?random={message_id}"
            response = requests.get(demo_url)
            return StreamingResponse(io.BytesIO(response.content), media_type="image/jpeg")
        
        # Get channel entity
        channel_entity = await telegram_client.client.get_entity(channel)
        
        # Get message
        message = await telegram_client.client.get_messages(channel_entity, ids=int(message_id))
        
        if message and message.media and isinstance(message.media, MessageMediaPhoto):
            # Download photo
            photo_bytes = await telegram_client.client.download_media(message.media, file=io.BytesIO())
            return StreamingResponse(io.BytesIO(photo_bytes), media_type="image/jpeg")
        else:
            # Return demo image if no photo
            demo_url = f"https://picsum.photos/400/600?random={message_id}"
            response = requests.get(demo_url)
            return StreamingResponse(io.BytesIO(response.content), media_type="image/jpeg")
            
    except Exception as e:
        logger.error(f"Error getting photo: {e}")
        # Return demo image on error
        demo_url = f"https://picsum.photos/400/600?random={message_id}"
        response = requests.get(demo_url)
        return StreamingResponse(io.BytesIO(response.content), media_type="image/jpeg")

@app.get("/ui", response_class=HTMLResponse)
async def ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Creative MVP</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .tabs { display: flex; justify-content: center; margin-bottom: 30px; }
            .tab { padding: 10px 20px; margin: 0 10px; background: #007bff; color: white; border: none; cursor: pointer; border-radius: 5px; }
            .tab.active { background: #0056b3; }
            .feed { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .post { background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .post-image { width: 100%; height: 200px; object-fit: cover; }
            .post-content { padding: 15px; }
            .post-text { margin-bottom: 10px; }
            .post-meta { font-size: 12px; color: #666; }
            .loading { text-align: center; padding: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Creative MVP</h1>
                <p>Реальные посты из Telegram каналов</p>
            </div>
            
            <div class="tabs">
                <button class="tab active" onclick="loadFeed('fashion')">Fashion</button>
            </div>
            
            <div id="feed" class="feed">
                <div class="loading">Загрузка...</div>
            </div>
        </div>

        <script>
            async function loadFeed(category) {
                const feed = document.getElementById('feed');
                feed.innerHTML = '<div class="loading">Загрузка...</div>';
                
                try {
                    const response = await fetch(`/api/feed/${category}?limit=6`);
                    const data = await response.json();
                    
                    feed.innerHTML = '';
                    data.posts.forEach(post => {
                        const postDiv = document.createElement('div');
                        postDiv.className = 'post';
                        postDiv.innerHTML = `
                            <img src="${post.media_url || 'https://picsum.photos/400/200?random=' + post.id}" 
                                 class="post-image" alt="Post image">
                            <div class="post-content">
                                <div class="post-text">${post.text}</div>
                                <div class="post-meta">
                                    @${post.channel} • ${post.views} просмотров • ${post.date}
                                </div>
                            </div>
                        `;
                        feed.appendChild(postDiv);
                    });
                } catch (error) {
                    feed.innerHTML = '<div class="loading">Ошибка загрузки</div>';
                }
            }
            
            // Load fashion feed by default
            loadFeed('fashion');
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Start server
echo "🎉 Starting server..."
python3 vps_server.py