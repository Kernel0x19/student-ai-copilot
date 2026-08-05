# ⚡ Redis Quick Start

## 🚀 5-Minute Setup

### **1. Install & Start Redis**

**Option A: Docker (Easiest)**
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

**Option B: WSL (Windows)**
```bash
wsl
sudo apt-get install redis-server
sudo service redis-server start
```

**Option C: Memurai (Windows Native)**
- Download: https://www.memurai.com/get-memurai
- Install and it runs automatically

---

### **2. Update Environment**

**Add to `services/.env`:**
```bash
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
```

---

### **3. Test Connection**

```bash
redis-cli ping
# Should return: PONG
```

---

### **4. Restart Backend**

```bash
cd services
uvicorn app.main:app --reload
```

**Done! Redis is now active.** ✅

---

## 🎯 What Redis Does for You

1. **Caches API Responses** - Faster page loads
2. **Handles Background Jobs** - Celery tasks (notifications, data sync)
3. **Rate Limiting** - Prevents API abuse
4. **Session Storage** - User sessions

---

## 💡 Quick Test

**Python test:**
```python
import redis

# Connect
r = redis.from_url("redis://localhost:6379/0")

# Test
r.set("test", "Hello Redis!")
print(r.get("test"))  # b'Hello Redis!'

# Success! ✅
```

---

## 🔍 Common Commands

```bash
# Check if running
redis-cli ping

# Start (Docker)
docker start redis

# Stop (Docker)
docker stop redis

# View all keys
redis-cli KEYS '*'

# Clear all cache
redis-cli FLUSHDB
```

---

## 📊 Usage in Code

### **Cache API Response**

```python
import redis
redis_client = redis.from_url(settings.redis_url)

# Cache for 1 hour
redis_client.setex(
    "recommendations:user-123",
    3600,
    json.dumps(data)
)

# Get from cache
cached = redis_client.get("recommendations:user-123")
```

### **Background Task (Celery)**

```python
from app.tasks import send_email

# Queue task (non-blocking)
task = send_email.delay("user@example.com", "Hello")

# Start worker (separate terminal)
# celery -A app.tasks worker --loglevel=info
```

---

## 🐛 Troubleshooting

**Connection refused?**
```bash
# Check if Redis is running
docker ps | grep redis

# Or
redis-cli ping
```

**Not working?**
1. Verify Redis is running
2. Check `.env` has correct `REDIS_URL`
3. Restart backend server
4. Check logs: `docker logs redis`

---

## 📚 Full Documentation

See **REDIS_SETUP_GUIDE.md** for:
- Detailed installation
- Advanced caching
- Pub/Sub patterns
- Production setup
- Monitoring

---

**Your Redis setup is complete!** 🎉

**Next:** Check `REDIS_SETUP_GUIDE.md` for advanced features.
