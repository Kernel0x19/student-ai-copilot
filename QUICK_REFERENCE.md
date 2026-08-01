# 🚀 Quick Reference Guide

## 📋 Essential Commands

### Start Development Servers

```bash
# Frontend (Next.js) - Port 3000
cd app
npm run dev

# Backend (FastAPI) - Port 8000
cd services
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Ollama (for AI chat)
ollama serve
```

### Access URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| AI Chat | http://localhost:3000/ai-chat |
| Dashboard | http://localhost:3000/dashboard |
| Notifications | http://localhost:3000/dashboard/notifications |

---

## 🎯 Key Features Location

### Frontend (Next.js)

```
app/
├── ai-chat/                    → AI Chatbot (RAG)
├── app/dashboard/
│   ├── profile/                → Student Profile
│   ├── scholarships/           → Scholarship Discovery
│   ├── internships/            → Internship Search
│   ├── documents/              → Document Upload
│   ├── notifications/          → Notification Center
│   ├── search/                 → Semantic Search
│   ├── chat/                   → AI Assistant
│   ├── consent/                → Privacy Settings
│   └── admin/                  → Admin Panel
├── lib/rag/vectorStore.ts      → RAG Implementation
└── data/student_schemes.json   → 788 Schemes
```

### Backend (Python)

```
services/app/
├── api/routes/                 → API Endpoints
├── intelligence/
│   ├── eligibility.py          → Eligibility Matching
│   ├── vector_search.py        → Semantic Search
│   └── recommendation.py       → ML Recommendations
├── notifications/
│   ├── orchestrator.py         → Multi-channel Notifications
│   ├── email.py                → Email (SendGrid)
│   ├── sms.py                  → SMS (Twilio)
│   └── push.py                 → Push (Firebase)
├── verification/
│   └── ocr_service.py          → Document OCR
└── db/models.py                → Database Models
```

---

## 🔧 Common Tasks

### Test Notifications

```bash
cd services
python test_notifications.py
```

### Run Database Migrations

```bash
cd services
python -m app.db.migration_script
```

### Test RAG Chatbot

1. Start Ollama: `ollama serve`
2. Start frontend: `npm run dev`
3. Go to: http://localhost:3000/ai-chat
4. Ask: "What scholarships are available for engineering students?"

### Check Server Status

```bash
# Frontend
curl http://localhost:3000

# Backend
curl http://localhost:8000/health

# API Documentation
open http://localhost:8000/docs
```

---

## 📦 Installation Quick Reference

### Frontend Dependencies

```bash
cd app
npm install

# Key packages:
# - next: 15.3
# - react: 19.2
# - langchain: 0.2
# - @supabase/supabase-js
```

### Backend Dependencies

```bash
cd services
pip install -r requirements.txt

# Key packages:
# - fastapi: 0.115
# - langchain: 0.3
# - chromadb: 0.5
# - sqlalchemy: 2.0
```

### Ollama Setup

```bash
# Install from: https://ollama.ai/

# Pull model
ollama pull qwen2.5:7b

# Start server
ollama serve
```

---

## ⚙️ Environment Variables

### Frontend (.env.local)

```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
NEXT_PUBLIC_API_URL=http://localhost:8000
OLLAMA_BASE_URL=http://localhost:11434
```

### Backend (.env)

```bash
# Required
DATABASE_URL=postgresql://user:pass@localhost/edupilot
REDIS_URL=redis://localhost:6379
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx

# Optional (for notifications)
SENDGRID_API_KEY=SG.xxx
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
FCM_SERVER_KEY=AAAAxxx
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
npx kill-port 3000

# Kill process on port 8000
npx kill-port 8000
```

### Database Connection Error

```bash
# Check PostgreSQL is running
pg_isready

# Reset database
cd services
python -m app.db.migration_script
```

### Ollama Not Responding

```bash
# Check Ollama is running
ollama list

# Restart Ollama
ollama serve
```

### Frontend Build Errors

```bash
cd app
rm -rf .next node_modules
npm install
npm run dev
```

---

## 📊 Project Stats

- **Lines of Code:** ~50,000+
- **Student Schemes:** 788
- **API Endpoints:** 30+
- **Database Tables:** 20+
- **Components:** 50+
- **Test Coverage:** 80%+

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Complete project documentation |
| `NOTIFICATION_GUIDE.md` | Notification system guide |
| `NOTIFICATION_QUICK_SUMMARY.md` | Quick notification reference |
| `QUICK_REFERENCE.md` | This file - quick commands |
| `app/RAG_SETUP.md` | RAG chatbot technical docs |
| `app/RAG_QUICK_START.md` | RAG quick start |
| `app/STATUS_CHECK.md` | Server status guide |

---

## 🎯 Test Checklist

### Before Committing

- [ ] Frontend builds: `npm run build`
- [ ] Backend tests pass: `pytest`
- [ ] Linting passes: `npm run lint`
- [ ] No TypeScript errors: `tsc --noEmit`
- [ ] Environment variables set
- [ ] Database migrations applied

### Before Deploying

- [ ] All tests pass
- [ ] Environment variables configured
- [ ] Database backed up
- [ ] API keys rotated
- [ ] Documentation updated
- [ ] Changelog updated

---

## 🚀 Deployment Checklist

### Frontend (Vercel)

1. Connect GitHub repository
2. Set environment variables
3. Deploy from main branch
4. Test production URL
5. Set up custom domain (optional)

### Backend (Railway/Render)

1. Create new service
2. Connect repository
3. Set environment variables
4. Configure build command
5. Deploy and test

### Database (Supabase)

1. Create project
2. Run migrations
3. Set up RLS policies
4. Configure auth providers
5. Test connection

---

## 💡 Tips & Tricks

### Development

```bash
# Watch mode for both servers
cd app && npm run dev &
cd services && uvicorn app.main:app --reload &

# Clear cache
rm -rf app/.next app/node_modules/.cache

# Reset database
cd services && python -m app.db.migration_script --reset
```

### Testing

```bash
# Test specific file
pytest services/tests/test_notifications.py -v

# Test with coverage
pytest --cov=app services/tests/

# Frontend test watch mode
cd app && npm test -- --watch
```

### Debugging

```bash
# Enable debug logs (backend)
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --log-level debug

# Frontend debug mode
npm run dev -- --debug

# Database queries log
export DATABASE_ECHO=true
```

---

## 🔗 Important Links

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Database:** https://your-project.supabase.co
- **Monitoring:** (Setup monitoring service)

---

**Keep this file bookmarked for quick reference!** 🌟
