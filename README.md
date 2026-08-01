# 🎓 EduPilot - AI-Powered Student Assistant Platform

**Your intelligent companion for scholarships, internships, and educational opportunities.**

[![Next.js](https://img.shields.io/badge/Next.js-15.3-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178c6)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📚 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Technologies](#-technologies)
- [Features Deep Dive](#-features-deep-dive)
- [Configuration](#-configuration)
- [Development](#-development)
- [Deployment](#-deployment)
- [Documentation](#-documentation)
- [Contributing](#-contributing)

---

## 🌟 Overview

**EduPilot** is an AI-powered platform that helps students discover, track, and apply for scholarships, internships, and educational opportunities. It uses advanced AI technologies including RAG (Retrieval Augmented Generation), semantic search, and eligibility matching to provide personalized recommendations.

### 🎯 Problem Solved

Students struggle with:
- Finding relevant scholarships among thousands of options
- Understanding complex eligibility criteria
- Tracking application deadlines
- Managing required documents
- Getting personalized recommendations

### 💡 Solution

EduPilot provides:
- **AI-Powered Search**: Semantic search through 788+ student schemes
- **Smart Matching**: Automatic eligibility checking
- **Personalized Recommendations**: ML-based opportunity matching
- **RAG Chatbot**: Natural language queries about schemes
- **Document Management**: Upload and verify documents with OCR
- **Deadline Tracking**: Automated reminders via Email/SMS/Push
- **Application Workflow**: Step-by-step application guidance

---

## ✨ Key Features

### 🤖 **AI & Intelligence**
- ✅ **RAG Chatbot** - Ask questions about 788+ schemes in natural language
- ✅ **Semantic Search** - Find opportunities using natural language queries
- ✅ **Smart Eligibility** - Automatic matching based on student profile
- ✅ **ML Recommendations** - Personalized opportunity suggestions
- ✅ **Document OCR** - Extract data from uploaded documents

### 📊 **Student Dashboard**
- ✅ **Profile Management** - Complete student profile with verification
- ✅ **Opportunity Discovery** - Browse scholarships, internships, grants
- ✅ **Application Tracking** - Monitor application status
- ✅ **Document Upload** - Secure document storage
- ✅ **Notification Center** - Multi-channel notifications

### 🔔 **Notification System**
- ✅ **In-App Notifications** - Real-time dashboard alerts
- ✅ **Email Notifications** - Via SendGrid (100 emails/day free)
- ✅ **SMS Alerts** - Via Twilio (urgent deadlines)
- ✅ **Push Notifications** - Browser/mobile via FCM
- ✅ **User Preferences** - Granular control over notifications

### 🔒 **Security & Privacy**
- ✅ **Authentication** - Supabase Auth (email/social login)
- ✅ **RBAC** - Role-based access control
- ✅ **Consent Management** - GDPR-compliant data handling
- ✅ **Document Encryption** - Secure document storage
- ✅ **Audit Logging** - Track all data access

### 📈 **Admin & Analytics**
- ✅ **Platform Analytics** - User engagement metrics
- ✅ **Data Freshness** - Monitor data quality
- ✅ **A/B Testing** - Experiment framework
- ✅ **Connector Status** - Data pipeline monitoring

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Dashboard│  │   Chat   │  │  Profile │  │  Search  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API / GraphQL
┌────────────────────────┴────────────────────────────────────┐
│                  BACKEND (FastAPI + Python)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Intelligence│  │ Notifications│  │  Ingestion   │     │
│  │  - RAG       │  │  - Email     │  │  - Connectors│     │
│  │  - Search    │  │  - SMS       │  │  - Normalizer│     │
│  │  - Eligibility  │  - Push      │  │  - Pipeline  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    DATA LAYER                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │  Chroma  │  │  Supabase│  │  Redis   │   │
│  │  (Main)  │  │ (Vectors)│  │  (Auth)  │  │ (Cache)  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- Next.js 15.3 (React 19)
- TypeScript 5.0
- Tailwind CSS 4
- LangChain.js (RAG chatbot)
- Lucide Icons

**Backend:**
- FastAPI 0.115
- Python 3.11+
- SQLAlchemy 2.0
- Pydantic 2.8
- Celery + Redis (async tasks)

**AI & ML:**
- LangChain + LangGraph
- Ollama (Local LLM)
- ChromaDB (Vector Store)
- Sentence Transformers
- RAG Pipeline

**Databases:**
- PostgreSQL (Primary)
- ChromaDB (Embeddings)
- Redis (Cache/Queue)
- Supabase (Auth)

**External Services:**
- SendGrid (Email)
- Twilio (SMS)
- Firebase (Push)
- OCR Services

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required
Node.js 18+ and npm
Python 3.11+
PostgreSQL 14+
Redis 7+

# Optional (for AI features)
Ollama (for local LLM)
Docker (for services)
```

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/student-ai-copilot.git
cd student-ai-copilot
```

### 2. Setup Frontend (Next.js)

```bash
cd app
npm install
cp .env.example .env.local

# Add your environment variables to .env.local:
# NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will run at: **http://localhost:3000**

### 3. Setup Backend (FastAPI)

```bash
cd services
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

# Add your environment variables to .env:
# DATABASE_URL=postgresql://user:pass@localhost/edupilot
# REDIS_URL=redis://localhost:6379
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_key

# Run database migrations
python -m app.db.migration_script

# Start development server
uvicorn app.main:app --reload --port 8000
```

Backend will run at: **http://localhost:8000**

### 4. Setup Ollama (Optional - for AI Chat)

```bash
# Install Ollama: https://ollama.ai/

# Pull the model
ollama pull qwen2.5:7b

# Start Ollama
ollama serve
```

### 5. Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **AI Chat:** http://localhost:3000/ai-chat
- **Dashboard:** http://localhost:3000/dashboard

---

## 📁 Project Structure

```
student-ai-copilot/
├── app/                          # Frontend (Next.js)
│   ├── app/                      # Next.js App Router
│   │   ├── api/                  # API routes
│   │   │   └── chat/             # RAG chatbot API
│   │   ├── auth/                 # Authentication pages
│   │   │   ├── login/
│   │   │   ├── signup/
│   │   │   └── callback/
│   │   ├── dashboard/            # User dashboard
│   │   │   ├── profile/          # Profile management
│   │   │   ├── scholarships/     # Scholarship discovery
│   │   │   ├── internships/      # Internship search
│   │   │   ├── documents/        # Document management
│   │   │   ├── notifications/    # Notification center
│   │   │   ├── search/           # Semantic search
│   │   │   ├── chat/             # AI chatbot
│   │   │   ├── consent/          # Privacy consent
│   │   │   └── admin/            # Admin panel
│   │   ├── components/           # React components
│   │   │   ├── dashboard/        # Dashboard components
│   │   │   └── home/             # Landing page components
│   │   ├── lib/                  # Utilities
│   │   │   ├── api.ts            # API client
│   │   │   ├── rag/              # RAG implementation
│   │   │   │   └── vectorStore.ts
│   │   │   └── supabase/         # Supabase clients
│   │   ├── ai-chat/              # AI chatbot page
│   │   ├── globals.css           # Global styles
│   │   ├── layout.tsx            # Root layout
│   │   └── page.tsx              # Home page
│   ├── data/                     # Knowledge base
│   │   ├── student_schemes.json  # 788 student schemes
│   │   └── student_schemes_index.json
│   ├── public/                   # Static assets
│   ├── package.json              # NPM dependencies
│   ├── tsconfig.json             # TypeScript config
│   ├── tailwind.config.ts        # Tailwind config
│   ├── RAG_SETUP.md             # RAG documentation
│   └── RAG_QUICK_START.md       # Quick start guide
│
├── services/                     # Backend (Python/FastAPI)
│   ├── app/
│   │   ├── agents/               # AI agents
│   │   │   ├── chatbot.py        # Conversational AI
│   │   │   └── scholarship.py    # Scholarship assistant
│   │   ├── analytics/            # Analytics & metrics
│   │   │   ├── event_service.py
│   │   │   ├── experiment_service.py
│   │   │   └── metrics_calculator.py
│   │   ├── api/                  # API routes
│   │   │   ├── routes/
│   │   │   │   ├── admin.py
│   │   │   │   ├── consent.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── feedback.py
│   │   │   │   ├── notifications.py
│   │   │   │   ├── profile.py
│   │   │   │   ├── scholarships.py
│   │   │   │   └── search.py
│   │   │   ├── middleware/
│   │   │   └── deps.py
│   │   ├── db/                   # Database
│   │   │   ├── models.py         # SQLAlchemy models
│   │   │   ├── session.py        # DB session
│   │   │   └── migrations/       # Alembic migrations
│   │   ├── ingestion/            # Data pipelines
│   │   │   ├── connectors/       # Data connectors
│   │   │   ├── pipeline.py
│   │   │   └── normalizer.py
│   │   ├── intelligence/         # AI/ML services
│   │   │   ├── eligibility.py    # Eligibility engine
│   │   │   ├── embeddings.py     # Vector embeddings
│   │   │   ├── recommendation.py # ML recommendations
│   │   │   └── vector_search.py  # Semantic search
│   │   ├── knowledge/            # Knowledge base
│   │   │   └── hybrid_rag.py     # RAG implementation
│   │   ├── notifications/        # Notification system
│   │   │   ├── service.py        # Base service
│   │   │   ├── orchestrator.py   # Multi-channel
│   │   │   ├── email.py          # SendGrid
│   │   │   ├── sms.py            # Twilio
│   │   │   ├── push.py           # FCM
│   │   │   └── deadline_monitor.py
│   │   ├── security/             # Security services
│   │   │   ├── consent.py        # Consent management
│   │   │   ├── document_store.py # Encrypted storage
│   │   │   ├── rbac.py           # Access control
│   │   │   └── tee.py            # Trusted execution
│   │   ├── verification/         # Document verification
│   │   │   ├── engine.py         # Verification engine
│   │   │   ├── ocr_service.py    # OCR processing
│   │   │   ├── gov_api.py        # Government APIs
│   │   │   └── parsers.py        # Document parsers
│   │   ├── workflow/             # Workflow engine
│   │   │   └── engine.py
│   │   ├── config.py             # Configuration
│   │   ├── main.py               # FastAPI app
│   │   └── tasks.py              # Celery tasks
│   ├── tests/                    # Test suite
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment template
│   └── Dockerfile                # Docker config
│
├── docs/                         # Documentation
├── chroma_data/                  # Vector database
├── .kiro/                        # Kiro AI config
├── docker-compose.yml            # Docker services
├── .gitignore
├── README.md                     # This file
├── NOTIFICATION_GUIDE.md         # Notification docs
├── NOTIFICATION_QUICK_SUMMARY.md
└── requirements.txt              # Root dependencies
```

---

## 🛠️ Technologies

### Frontend Stack
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 15.3 | React framework |
| React | 19.2 | UI library |
| TypeScript | 5.0 | Type safety |
| Tailwind CSS | 4.0 | Styling |
| LangChain.js | 0.2 | RAG chatbot |
| Supabase | 2.110 | Auth & database |
| Lucide Icons | 1.26 | Icon library |

### Backend Stack
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.115 | Web framework |
| Python | 3.11+ | Backend language |
| SQLAlchemy | 2.0 | ORM |
| Pydantic | 2.8 | Data validation |
| Celery | 5.4 | Task queue |
| Redis | 5.2 | Cache/queue |

### AI & ML Stack
| Technology | Version | Purpose |
|------------|---------|---------|
| LangChain | 0.3 | LLM framework |
| LangGraph | 0.2 | Agent workflows |
| Ollama | - | Local LLM |
| ChromaDB | 0.5 | Vector database |
| Sentence Transformers | 2.2+ | Embeddings |

### External Services
| Service | Purpose | Free Tier |
|---------|---------|-----------|
| Supabase | Auth & Database | Yes (500MB) |
| SendGrid | Email | Yes (100/day) |
| Twilio | SMS | Trial ($15) |
| Firebase | Push notifications | Yes |

---

## 🎨 Features Deep Dive

### 1. RAG-Powered AI Chatbot

**Location:** `app/ai-chat/page.tsx`

Ask natural language questions about 788+ student schemes:

```typescript
// Example queries:
"What scholarships are available for engineering students in Karnataka?"
"Tell me about AICTE schemes with deadlines in December"
"Which schemes don't require a caste certificate?"
```

**How it works:**
1. User query → Vector store search (semantic similarity)
2. Retrieve top 3 relevant schemes
3. Build context with scheme details
4. Send to Ollama LLM with context
5. Return AI-generated answer + sources

**Documentation:** `app/RAG_SETUP.md`

### 2. Semantic Search

**Location:** `services/app/intelligence/vector_search.py`

Search opportunities using natural language:

```python
# Example: Search for "computer science internships with stipend"
results = await search_opportunities_semantic(
    query="computer science internships with stipend",
    category="internship",
    top_k=20
)
```

**Features:**
- Natural language understanding
- Category filtering
- Relevance scoring
- Fast vector similarity search

### 3. Smart Eligibility Matching

**Location:** `services/app/intelligence/eligibility.py`

Automatic eligibility checking based on:
- Academic qualifications
- Income criteria
- Category (SC/ST/OBC/General)
- State/location
- Age limits
- Course/degree type

**Example:**
```python
result = check_eligibility(
    student_profile={
        "category": "SC",
        "income_annual": 250000,
        "state": "Karnataka",
        "degree": "B.Tech",
        "cgpa": 8.5
    },
    opportunity_rules={
        "category": ["SC", "ST"],
        "income_max": 300000,
        "states": ["Karnataka"],
        "min_cgpa": 7.0
    }
)
# Returns: {"eligible": True, "score": 0.95, "reasons": [...]}
```

### 4. Multi-Channel Notifications

**Location:** `services/app/notifications/`

Send notifications via multiple channels based on user preferences:

**Channels:**
- **In-App:** Database-stored notifications
- **Email:** Via SendGrid API
- **SMS:** Via Twilio API
- **Push:** Via Firebase Cloud Messaging

**Types:**
- ⏰ Deadline reminders (7-day, 2-day)
- ✨ New opportunity matches
- 📊 Application status updates

**User Controls:**
- Toggle each channel on/off
- Toggle each notification type
- All preferences stored per user

**Documentation:** `NOTIFICATION_GUIDE.md`

### 5. Document Verification

**Location:** `services/app/verification/`

Upload and verify documents with OCR:

**Supported Documents:**
- Aadhaar Card
- PAN Card
- Income Certificate
- Caste Certificate
- Educational Certificates
- Bank Statements

**Process:**
1. Upload document
2. OCR extraction (Tesseract/Cloud)
3. Field validation
4. Government API verification (optional)
5. Store encrypted

### 6. Admin Dashboard

**Location:** `app/app/dashboard/admin/`

Monitor platform health and metrics:

**Features:**
- Platform KPIs (users, applications, etc.)
- Data freshness monitoring
- Connector status
- Accuracy metrics
- A/B test results
- Audit logs

---

## ⚙️ Configuration

### Frontend Environment Variables

Create `app/.env.local`:

```bash
# Supabase (Required)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

# Backend API (Required)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Ollama (Optional - for AI chat)
OLLAMA_BASE_URL=http://localhost:11434
```

### Backend Environment Variables

Create `services/.env`:

```bash
# Database (Required)
DATABASE_URL=postgresql://user:password@localhost:5432/edupilot

# Redis (Required)
REDIS_URL=redis://localhost:6379

# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key

# Email (Optional - SendGrid)
SENDGRID_API_KEY=SG.your_api_key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=EduPilot

# SMS (Optional - Twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Push (Optional - Firebase)
FCM_SERVER_KEY=AAAAxxxxxxxx
FCM_SENDER_ID=123456789012

# Ollama (Optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# ChromaDB (Optional)
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Security
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_32_byte_encryption_key

# Government APIs (Optional)
DIGILOCKER_CLIENT_ID=your_client_id
DIGILOCKER_CLIENT_SECRET=your_client_secret
```

---

## 👨‍💻 Development

### Run Frontend

```bash
cd app
npm run dev
```

### Run Backend

```bash
cd services
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000
```

### Run Celery Worker

```bash
cd services
celery -A app.tasks worker --loglevel=info
```

### Run Tests

**Frontend:**
```bash
cd app
npm test
```

**Backend:**
```bash
cd services
pytest tests/ -v
```

### Database Migrations

```bash
cd services
python -m app.db.migration_script
```

### Test Notifications

```bash
cd services
python test_notifications.py
```

---

## 🚢 Deployment

### Docker Deployment

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Deployment

**Frontend (Vercel/Netlify):**
```bash
cd app
npm run build
# Deploy build to hosting platform
```

**Backend (Railway/Render/AWS):**
```bash
cd services
# Follow platform-specific deployment guide
```

---

## 📖 Documentation

### Main Documentation
- **README.md** (this file) - Complete project overview
- **NOTIFICATION_GUIDE.md** - Notification system guide
- **NOTIFICATION_QUICK_SUMMARY.md** - Quick notification reference

### Frontend Documentation
- **app/RAG_SETUP.md** - RAG chatbot technical docs
- **app/RAG_QUICK_START.md** - Quick start for RAG
- **app/STATUS_CHECK.md** - Server status guide
- **app/AGENTS.md** - AI agent documentation
- **app/CLAUDE.md** - Claude integration notes

### Backend Documentation
- **services/app/notifications/README.md** - Notification services
- **services/app/verification/README_OCR.md** - OCR setup
- **services/app/security/README_TEE.md** - Trusted execution
- **services/app/ingestion/README_ORCHESTRATOR.md** - Data pipelines
- **services/POSTGRESQL_CONFIGURATION_GUIDE.md** - Database setup

### API Documentation
- **Interactive API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Setup Development Environment

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `npm test` and `pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style

**Frontend (TypeScript/React):**
- Use TypeScript strict mode
- Follow React hooks best practices
- Use Tailwind CSS for styling
- ESLint configuration included

**Backend (Python):**
- Follow PEP 8 style guide
- Use type hints (mypy)
- Write docstrings for functions
- Use async/await where appropriate

### Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Next.js** - Amazing React framework
- **FastAPI** - Fast and modern Python web framework
- **LangChain** - Powerful LLM framework
- **Ollama** - Easy local LLM deployment
- **Supabase** - Backend as a service
- **Tailwind CSS** - Utility-first CSS framework

---

## 📞 Support

- **Documentation:** Check the docs in each directory
- **Issues:** Open an issue on GitHub
- **Email:** support@edupilot.com (if available)

---

## 🗺️ Roadmap

### Current Features ✅
- ✅ RAG-powered AI chatbot (788 schemes)
- ✅ Semantic search
- ✅ Smart eligibility matching
- ✅ Multi-channel notifications
- ✅ Document upload & OCR
- ✅ User dashboard
- ✅ Admin analytics

### Upcoming Features 🚀
- 🔄 Mobile app (React Native)
- 🔄 Voice assistant
- 🔄 Blockchain verification
- 🔄 AI resume builder
- 🔄 Interview preparation
- 🔄 Career guidance
- 🔄 Alumni network

---

## 📊 Stats

- **Total Student Schemes:** 788+
- **Categories:** Scholarships, Internships, Grants, Skill Development
- **States Covered:** All Indian states
- **Ministries:** 20+ government departments
- **Languages:** English, Hindi (more coming)

---

**Made with ❤️ for students by students**

**⭐ Star this repo if you find it helpful!**