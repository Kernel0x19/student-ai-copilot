# 🚀 Project Setup Guide - Student AI Copilot

Complete guide to run the Student AI Copilot project from scratch.

---

## 📋 **PREREQUISITES**

### Required Software:
1. **Python 3.10+** - Backend runtime
2. **Node.js 18+** - Frontend runtime
3. **Docker Desktop** - For PostgreSQL + Redis
4. **Git** - Version control

### Check if installed:
```bash
python --version    # Should show 3.10 or higher
node --version      # Should show v18 or higher
npm --version       # Should show npm version
docker --version    # Should show Docker version
```

---

## 🛠️ **INSTALLATION STEPS**

### **STEP 1: Clone & Navigate**
```bash
cd d:\student\student-ai-copilot
```

---

### **STEP 2: Start Docker Services (PostgreSQL + Redis)**

#### Start containers:
```bash
docker-compose up -d postgres redis
```

#### Verify containers are running:
```bash
docker ps
```

You should see:
- `pgvector/pgvector:pg16` on port **5433**
- `redis:7-alpine` on port **6379**

#### **Services Now Running:**
- ✅ PostgreSQL: `localhost:5433`
- ✅ Redis: `localhost:6379`

---

### **STEP 3: Backend Setup (Python FastAPI)**

#### 3.1 Navigate to services folder:
```bash
cd services
```

#### 3.2 Create Python virtual environment:
```bash
python -m venv venv
```

#### 3.3 Activate virtual environment:
```bash
# Windows CMD:
venv\Scripts\activate

# Windows PowerShell:
venv\Scripts\Activate.ps1
```

You should see `(venv)` in your terminal prompt.

#### 3.4 Install Python dependencies:
```bash
pip install -r requirements.txt
```

**This installs:**
- FastAPI, Uvicorn (API server)
- SQLAlchemy, psycopg2 (Database)
- Celery, Redis (Background tasks)
- Playwright, BeautifulSoup (Web scraping)
- LangChain, Ollama (AI/LLM)
- ChromaDB (Vector database)
- And many more...

#### 3.5 Install Playwright browsers:
```bash
playwright install chromium
```

This downloads Chromium browser (~100MB) for web scraping.

#### 3.6 Verify `.env` file exists:
```bash
type .env
```

**Your `.env` should have:**
```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_USER=postgres
POSTGRES_PASSWORD=2777
POSTGRES_DB=edupilot
DATABASE_URL=postgresql://postgres:2777@localhost:5433/edupilot

# Redis
REDIS_URL=redis://localhost:6379/0

# Supabase (Authentication)
SUPABASE_URL=your_supabase_url
SUPABASE_JWT_SECRET=your_jwt_secret

# Ollama (LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gpt-oss:120b-cloud

# Optional: Notification services
SENDGRID_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_PHONE=
```

#### 3.7 Run database migration:
```bash
python -m app.db.migration_script
```

**This creates:**
- All database tables (users, opportunities, applications, etc.)
- Seeds 7 sample scholarships
- Sets up database schema

#### 3.8 Start Backend API:
```bash
uvicorn app.main:app --reload --port 8000
```

**Backend now running:** http://localhost:8000

#### **Verify Backend:**
Open browser: http://localhost:8000/docs (FastAPI Swagger UI)

---

### **STEP 4: Frontend Setup (Next.js)**

#### 4.1 Open NEW terminal (keep backend running)

#### 4.2 Navigate to app folder:
```bash
cd d:\student\student-ai-copilot\app
```

#### 4.3 Install Node.js dependencies:
```bash
npm install
```

**This installs:**
- Next.js 15 (React framework)
- Supabase client (Authentication)
- TailwindCSS (Styling)
- Lucide icons
- TypeScript

#### 4.4 Verify `.env` file exists:
```bash
type .env
```

**Your `app/.env` should have:**
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 4.5 Start Frontend:
```bash
npm run dev
```

**Frontend now running:** http://localhost:3001

(Port 3001 because 3000 might be in use)

#### **Verify Frontend:**
Open browser: http://localhost:3001

---

### **STEP 5: Start Celery Worker (Background Tasks)**

#### 5.1 Open NEW terminal (keep backend + frontend running)

#### 5.2 Navigate to services and activate venv:
```bash
cd d:\student\student-ai-copilot\services
venv\Scripts\activate
```

#### 5.3 Start Celery worker:
```bash
celery -A app.tasks worker --pool=solo -l info
```

**Note:** Windows requires `--pool=solo` flag

**Celery now running** and ready to process:
- Data connector tasks (AICTE scraping)
- Document verification tasks
- Notification tasks

---

### **STEP 6 (Optional): Start Celery Beat (Scheduled Tasks)**

#### 6.1 Open ANOTHER NEW terminal:
```bash
cd d:\student\student-ai-copilot\services
venv\Scripts\activate
```

#### 6.2 Start Celery Beat scheduler:
```bash
celery -A app.tasks beat -l info
```

**Celery Beat now running** and will:
- Run data connectors daily at 2 AM
- Scan deadlines every hour
- Send notifications automatically

---

## ✅ **VERIFICATION CHECKLIST**

After all steps, you should have **6 terminals running:**

| Terminal | Service | Command | Port | Status |
|----------|---------|---------|------|--------|
| 1 | Docker (Postgres+Redis) | `docker-compose up -d postgres redis` | 5433, 6379 | Background |
| 2 | Backend API | `uvicorn app.main:app --reload --port 8000` | 8000 | Running |
| 3 | Frontend | `npm run dev` | 3001 | Running |
| 4 | Celery Worker | `celery -A app.tasks worker --pool=solo -l info` | - | Running |
| 5 | Celery Beat (Optional) | `celery -A app.tasks beat -l info` | - | Running |

### **Test URLs:**
- ✅ Backend API: http://localhost:8000/docs
- ✅ Frontend: http://localhost:3001
- ✅ Health Check: http://localhost:8000/health

---

## 🎯 **QUICK START COMMANDS**

### **Start Everything (Daily Workflow):**

#### Terminal 1 - Docker:
```bash
cd d:\student\student-ai-copilot
docker-compose up -d postgres redis
```

#### Terminal 2 - Backend:
```bash
cd d:\student\student-ai-copilot\services
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

#### Terminal 3 - Frontend:
```bash
cd d:\student\student-ai-copilot\app
npm run dev
```

#### Terminal 4 - Celery Worker:
```bash
cd d:\student\student-ai-copilot\services
venv\Scripts\activate
celery -A app.tasks worker --pool=solo -l info
```

---

## 🛑 **STOP EVERYTHING**

### Stop services:
```bash
# In each terminal, press: Ctrl + C

# Stop Docker containers:
docker-compose down
```

---

## 🔧 **TROUBLESHOOTING**

### **Problem 1: Port already in use**

**Error:** `Address already in use: 8000`

**Solution:**
```bash
# Find process using port 8000:
netstat -ano | findstr :8000

# Kill process (replace PID):
taskkill /PID <process_id> /F
```

### **Problem 2: Database connection failed**

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check Docker containers:
docker ps

# Restart containers:
docker-compose down
docker-compose up -d postgres redis
```

### **Problem 3: Module not found**

**Error:** `ModuleNotFoundError: No module named 'pydantic_settings'`

**Solution:**
```bash
cd services
venv\Scripts\activate
pip install -r requirements.txt
```

### **Problem 4: Playwright browser not found**

**Error:** `Executable doesn't exist at C:\Users\...\chromium`

**Solution:**
```bash
cd services
venv\Scripts\activate
playwright install chromium
```

### **Problem 5: Migration fails**

**Error:** `relation "users" does not exist`

**Solution:**
```bash
cd services
venv\Scripts\activate
python -m app.db.migration_script
```

---

## 📁 **PROJECT STRUCTURE**

```
student-ai-copilot/
├── services/              # Backend (Python FastAPI)
│   ├── app/
│   │   ├── main.py       # API entry point
│   │   ├── tasks.py      # Celery tasks
│   │   ├── agents/       # AI agents (chatbot, scholarship)
│   │   ├── ingestion/    # Data connectors (AICTE, Unstop)
│   │   ├── knowledge/    # RAG, vector search
│   │   └── db/           # Database models, migration
│   ├── requirements.txt
│   ├── .env             # Backend environment variables
│   └── venv/            # Python virtual environment
│
├── app/                  # Frontend (Next.js)
│   ├── app/
│   │   ├── dashboard/   # Student dashboard
│   │   ├── components/  # React components
│   │   └── lib/         # Supabase client
│   ├── package.json
│   └── .env             # Frontend environment variables
│
├── docker-compose.yml    # PostgreSQL + Redis
├── README.md
└── SETUP_GUIDE.md       # This file
```

---

## 🚀 **NEXT STEPS**

1. **Create Account:**
   - Visit http://localhost:3001
   - Click "Sign Up"
   - Create student account

2. **Explore Dashboard:**
   - Profile → Fill your details (CGPA, category, etc.)
   - Scholarships → View matched scholarships
   - Chat → Ask AI chatbot questions
   - Search → Semantic search for opportunities

3. **Admin Features:**
   - Login as admin
   - Dashboard → Admin
   - Run data connectors
   - View analytics

4. **Test AI Features:**
   - Make sure Ollama is running: http://localhost:11434
   - Chat with AI copilot
   - Get scholarship recommendations

---

## 📚 **DOCUMENTATION**

- **Architecture:** `ARCHITECTURE.md`
- **API Reference:** http://localhost:8000/docs
- **Redis Guide:** `REDIS_QUICK_START.md`
- **Quick Reference:** `QUICK_REFERENCE.md`

---

## 🆘 **NEED HELP?**

- Check logs in each terminal for error messages
- Verify Docker containers: `docker ps`
- Check database: `docker exec -it <postgres_container> psql -U postgres -d edupilot`
- Restart services if issues persist

---

## ✨ **SUMMARY**

**Minimum to run:**
1. Docker (PostgreSQL + Redis)
2. Backend (FastAPI)
3. Frontend (Next.js)

**For full features:**
4. Celery Worker (background tasks)
5. Celery Beat (scheduled tasks)
6. Ollama (AI/LLM features)

**Happy coding! 🎉**
