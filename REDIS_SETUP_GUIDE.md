# 🚀 Redis Setup & Usage Guide

## 📋 What is Redis?

**Redis** (Remote Dictionary Server) is an in-memory data structure store used as:
- **Cache** - Store frequently accessed data for fast retrieval
- **Session Store** - Store user sessions
- **Message Queue** - For Celery background tasks
- **Rate Limiting** - Control API request rates
- **Real-time Data** - Pub/Sub for real-time features

---

## 🎯 How EduPilot Uses Redis

Your project is configured to use Redis for:

1. **Caching** - API responses, database queries
2. **Celery Queue** - Background tasks (notifications, data ingestion)
3. **Session Management** - User sessions
4. **Rate Limiting** - API throttling

---

## 📦 Installation

### **Option 1: Windows (Recommended)**

#### **A. Using Docker (Easiest)**

```bash
# Start Redis with Docker
docker run -d --name redis -p 6379:6379 redis:latest

# Check if running
docker ps | grep redis

# Stop Redis
docker stop redis

# Start Redis
docker start redis
```

#### **B. Using Windows Subsystem for Linux (WSL)**

```bash
# Open WSL terminal
wsl

# Install Redis
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo service redis-server start

# Check status
redis-cli ping
# Should return: PONG
```

#### **C. Using Memurai (Redis for Windows)**

1. Download from: https://www.memurai.com/get-memurai
2. Install the .msi file
3. Redis runs as a Windows service automatically
4. Default port: 6379

---

### **Option 2: Mac**

```bash
# Using Homebrew
brew install redis

# Start Redis
brew services start redis

# Check if running
redis-cli ping
# Should return: PONG

# Stop Redis
brew services stop redis
```

---

### **Option 3: Linux**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server

# Enable on boot
sudo systemctl enable redis-server

# Check status
sudo systemctl status redis-server
```

---

## ⚙️ Configuration

### **1. Update Environment Variables**

**Backend** (`services/.env`):
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Leave empty for local development

# For Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

**Frontend** (`app/.env.local`):
```bash
# If needed for Next.js caching
REDIS_URL=redis://localhost:6379/0
```

---

### **2. Verify Installation**

```bash
# Test Redis connection
redis-cli ping

# Should return: PONG

# Try basic commands
redis-cli
> SET test "Hello Redis"
> GET test
> DEL test
> EXIT
```

---

## 🔧 How to Use Redis in Your Project

### **1. Caching API Responses**

**File:** `services/app/api/routes/scholarships.py`

```python
import redis
from app.config import get_settings

settings = get_settings()
redis_client = redis.from_url(settings.redis_url)

@router.get("/scholarships/recommendations")
async def get_recommendations(user_id: str):
    cache_key = f"recommendations:{user_id}"
    
    # Try to get from cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # If not cached, fetch from database
    recommendations = await fetch_recommendations(user_id)
    
    # Store in cache for 1 hour (3600 seconds)
    redis_client.setex(
        cache_key,
        3600,
        json.dumps(recommendations)
    )
    
    return recommendations
```

---

### **2. Rate Limiting**

**File:** `services/app/api/middleware/rate_limit.py`

```python
from fastapi import HTTPException
import redis
import time

redis_client = redis.from_url(settings.redis_url)

def rate_limit(user_id: str, max_requests: int = 100, window: int = 60):
    """
    Rate limit: max_requests per window (seconds)
    """
    key = f"rate_limit:{user_id}"
    current = redis_client.get(key)
    
    if current is None:
        # First request in window
        redis_client.setex(key, window, 1)
        return True
    
    if int(current) >= max_requests:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )
    
    redis_client.incr(key)
    return True

# Usage in API route
@router.post("/api/v1/chat")
async def chat(request: ChatRequest, user_id: str):
    rate_limit(user_id, max_requests=10, window=60)  # 10 requests per minute
    # ... rest of the endpoint
```

---

### **3. Session Management**

**File:** `services/app/api/deps.py`

```python
import redis
import json
from datetime import timedelta

redis_client = redis.from_url(settings.redis_url)

def create_session(user_id: str, session_data: dict):
    """Create user session"""
    session_key = f"session:{user_id}"
    redis_client.setex(
        session_key,
        timedelta(hours=24),  # Session expires in 24 hours
        json.dumps(session_data)
    )

def get_session(user_id: str):
    """Get user session"""
    session_key = f"session:{user_id}"
    data = redis_client.get(session_key)
    return json.loads(data) if data else None

def delete_session(user_id: str):
    """Delete user session (logout)"""
    session_key = f"session:{user_id}"
    redis_client.delete(session_key)
```

---

### **4. Celery Background Tasks**

**File:** `services/app/tasks.py`

```python
from celery import Celery
from app.config import get_settings

settings = get_settings()

# Initialize Celery with Redis as broker and result backend
celery_app = Celery(
    "edupilot",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

@celery_app.task
def send_notification_email(user_id: str, title: str, body: str):
    """Background task to send email"""
    from app.notifications.email import EmailNotificationService
    
    email_service = EmailNotificationService()
    # Send email...
    return {"status": "sent", "user_id": user_id}

@celery_app.task
def generate_recommendations(user_id: str):
    """Background task to generate recommendations"""
    # Heavy computation...
    return {"user_id": user_id, "recommendations": [...]}

# Usage in API
from app.tasks import send_notification_email

@router.post("/notify")
async def notify_user(user_id: str):
    # Queue the task (non-blocking)
    task = send_notification_email.delay(user_id, "Test", "Hello")
    return {"task_id": task.id, "status": "queued"}
```

**Start Celery Worker:**
```bash
cd services
celery -A app.tasks worker --loglevel=info
```

---

### **5. Caching Database Queries**

**File:** `services/app/intelligence/recommendation.py`

```python
import redis
import json
from functools import wraps

redis_client = redis.from_url(settings.redis_url)

def cache_result(expire: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try cache first
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, expire, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage
@cache_result(expire=1800)  # Cache for 30 minutes
async def get_user_recommendations(user_id: str):
    """Get recommendations (cached)"""
    # Expensive database query...
    return recommendations
```

---

### **6. Real-time Notifications (Pub/Sub)**

**File:** `services/app/notifications/realtime.py`

```python
import redis
import json

redis_client = redis.from_url(settings.redis_url)

class RealtimeNotifier:
    def __init__(self):
        self.pubsub = redis_client.pubsub()
    
    def publish(self, user_id: str, message: dict):
        """Publish notification to user channel"""
        channel = f"notifications:{user_id}"
        redis_client.publish(channel, json.dumps(message))
    
    def subscribe(self, user_id: str):
        """Subscribe to user notifications"""
        channel = f"notifications:{user_id}"
        self.pubsub.subscribe(channel)
        return self.pubsub
    
    def listen(self, user_id: str):
        """Listen for notifications"""
        pubsub = self.subscribe(user_id)
        for message in pubsub.listen():
            if message['type'] == 'message':
                yield json.loads(message['data'])

# Usage
notifier = RealtimeNotifier()

# Publish notification
notifier.publish("user-123", {
    "title": "New Match",
    "body": "A new scholarship matches your profile"
})

# Listen for notifications (in a separate process/websocket)
for notification in notifier.listen("user-123"):
    print(notification)
```

---

## 🛠️ Common Redis Operations

### **Basic Commands**

```python
import redis

redis_client = redis.from_url("redis://localhost:6379/0")

# SET/GET
redis_client.set("key", "value")
value = redis_client.get("key")  # Returns bytes
value_str = redis_client.get("key").decode()  # Convert to string

# SET with expiration (seconds)
redis_client.setex("key", 60, "value")  # Expires in 60 seconds

# GET with default
value = redis_client.get("key") or "default_value"

# DELETE
redis_client.delete("key")

# EXISTS
exists = redis_client.exists("key")  # Returns 1 if exists, 0 if not

# INCREMENT/DECREMENT
redis_client.set("counter", 0)
redis_client.incr("counter")  # Increment by 1
redis_client.incrby("counter", 5)  # Increment by 5
redis_client.decr("counter")  # Decrement by 1

# EXPIRE (set expiration on existing key)
redis_client.expire("key", 300)  # Expires in 300 seconds

# TTL (get time to live)
ttl = redis_client.ttl("key")  # Returns seconds until expiration
```

---

### **Hash Operations (Key-Value within a Key)**

```python
# Store user data as hash
redis_client.hset("user:123", mapping={
    "name": "John Doe",
    "email": "john@example.com",
    "role": "student"
})

# Get single field
name = redis_client.hget("user:123", "name")

# Get all fields
user_data = redis_client.hgetall("user:123")

# Update single field
redis_client.hset("user:123", "email", "new@example.com")

# Delete field
redis_client.hdel("user:123", "role")
```

---

### **List Operations**

```python
# Push to list
redis_client.lpush("notifications:user:123", "Notification 1")
redis_client.lpush("notifications:user:123", "Notification 2")

# Get list items
notifications = redis_client.lrange("notifications:user:123", 0, -1)

# Get list length
length = redis_client.llen("notifications:user:123")

# Pop from list
notification = redis_client.lpop("notifications:user:123")
```

---

### **Set Operations**

```python
# Add to set
redis_client.sadd("user:123:interests", "engineering", "science", "ai")

# Check membership
is_member = redis_client.sismember("user:123:interests", "engineering")

# Get all members
interests = redis_client.smembers("user:123:interests")

# Remove from set
redis_client.srem("user:123:interests", "ai")
```

---

## 🔍 Monitoring Redis

### **Redis CLI Commands**

```bash
# Connect to Redis
redis-cli

# Get all keys
KEYS *

# Get keys matching pattern
KEYS user:*

# Get info about Redis
INFO

# Monitor all commands in real-time
MONITOR

# Get memory usage
MEMORY USAGE key_name

# Flush all data (CAREFUL!)
FLUSHALL

# Flush current database only
FLUSHDB
```

---

### **Check Redis Status**

```python
# In Python
import redis

redis_client = redis.from_url("redis://localhost:6379/0")

# Ping Redis
response = redis_client.ping()  # Returns True if connected

# Get info
info = redis_client.info()
print(f"Redis version: {info['redis_version']}")
print(f"Used memory: {info['used_memory_human']}")
print(f"Connected clients: {info['connected_clients']}")

# Get database size
db_size = redis_client.dbsize()
print(f"Total keys: {db_size}")
```

---

## 🐛 Debugging Redis

### **Check if Redis is Running**

```bash
# Test connection
redis-cli ping

# If you get "PONG", Redis is running
# If you get "Connection refused", Redis is not running
```

---

### **View Cached Data**

```python
import redis

redis_client = redis.from_url("redis://localhost:6379/0")

# List all keys
keys = redis_client.keys("*")
for key in keys:
    print(f"{key}: {redis_client.get(key)}")

# Get specific key
value = redis_client.get("recommendations:user-123")
print(value)

# Delete specific key
redis_client.delete("recommendations:user-123")
```

---

### **Clear All Cache**

```python
# Clear all keys in current database
redis_client.flushdb()

# Clear all keys in ALL databases
redis_client.flushall()
```

---

## 📊 Redis in Docker Compose

Your `docker-compose.yml` already has Redis configured:

```yaml
version: '3.8'

services:
  redis:
    image: redis:latest
    container_name: edupilot-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  backend:
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0

volumes:
  redis_data:
```

**Start with Docker Compose:**
```bash
docker-compose up -d redis
```

---

## 🎯 Quick Start Checklist

### **Development Setup:**

- [ ] Install Redis (Docker/WSL/Native)
- [ ] Start Redis: `docker start redis` or `redis-server`
- [ ] Test connection: `redis-cli ping`
- [ ] Update `services/.env` with `REDIS_URL=redis://localhost:6379/0`
- [ ] Restart your backend: `uvicorn app.main:app --reload`
- [ ] Test caching in your app

### **Production Setup:**

- [ ] Use managed Redis (AWS ElastiCache, Redis Cloud, Upstash)
- [ ] Set strong password in `REDIS_URL`
- [ ] Enable SSL/TLS
- [ ] Set up monitoring
- [ ] Configure persistence

---

## 🚀 Next Steps

1. **Start Redis**: Choose installation method above
2. **Update .env**: Add `REDIS_URL=redis://localhost:6379/0`
3. **Restart backend**: Your app will now use Redis for caching
4. **Test it**: API responses will be faster on second request
5. **Start Celery** (optional): For background tasks

---

## 📚 Useful Resources

- **Redis Documentation**: https://redis.io/documentation
- **Redis Python Client**: https://redis-py.readthedocs.io/
- **Celery Documentation**: https://docs.celeryproject.org/
- **Redis GUI Tools**: 
  - RedisInsight: https://redis.com/redis-enterprise/redis-insight/
  - Another Redis Desktop Manager: https://github.com/qishibo/AnotherRedisDesktopManager

---

**Redis is now ready to use in your EduPilot project!** 🎉
