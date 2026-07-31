# 🏗️ System Architecture

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Dashboard │  │ AI Chat  │  │  Search  │  │ Profile  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
┌───────┴─────────────┴─────────────┴─────────────┴──────────────┐
│                    FRONTEND (Next.js 15)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Components  │  Pages  │  API Routes  │  RAG  │  Utils  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │ REST API / JSON
┌────────────────────────────┴─────────────────────────────────────┐
│                  BACKEND (FastAPI + Python)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Intelligence │  │ Notifications│  │  Ingestion   │          │
│  │  - RAG       │  │  - Email     │  │  - Scraping  │          │
│  │  - Search    │  │  - SMS       │  │  - ETL       │          │
│  │  - Matching  │  │  - Push      │  │  - Pipeline  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐          │
│  │ Verification │  │   Security   │  │   Workflow   │          │
│  │  - OCR       │  │  - RBAC      │  │  - Engine    │          │
│  │  - Gov APIs  │  │  - Consent   │  │  - Tasks     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────┐
│                        DATA LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │PostgreSQL│  │  Chroma  │  │ Supabase │  │  Redis   │        │
│  │(Relational│  │ (Vectors)│  │  (Auth)  │  │ (Cache)  │        │
│  │   Data)  │  │          │  │          │  │          │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└──────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │SendGrid  │  │  Twilio  │  │ Firebase │  │  Ollama  │        │
│  │ (Email)  │  │  (SMS)   │  │  (Push)  │  │  (LLM)   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. User Query Flow (RAG Chatbot)

```
User Query
    ↓
Frontend (Next.js)
    ↓
API Route (/api/chat)
    ↓
Vector Store Search
    ↓
Retrieve Top K Documents
    ↓
Build Context
    ↓
Ollama LLM
    ↓
Generate Response
    ↓
Return with Sources
    ↓
Display to User
```

### 2. Semantic Search Flow

```
User Search Query
    ↓
Frontend Search Page
    ↓
Backend API (/api/v1/search)
    ↓
Embedding Generation
    ↓
ChromaDB Vector Search
    ↓
Similarity Scoring
    ↓
Filter & Rank Results
    ↓
Return Matches
    ↓
Display Results
```

### 3. Eligibility Matching Flow

```
Student Profile
    ↓
Get Opportunities
    ↓
For Each Opportunity:
    ├─> Check Category Match
    ├─> Check Income Criteria
    ├─> Check Location Match
    ├─> Check Academic Requirements
    ├─> Check Age Limits
    └─> Calculate Match Score
    ↓
Sort by Match Score
    ↓
Return Recommendations
```

### 4. Notification Flow

```
Trigger Event
(Deadline, Match, Status)
    ↓
Notification Orchestrator
    ↓
Check User Preferences
    ↓
Select Channels
    ├─> In-App → Database
    ├─> Email  → SendGrid API
    ├─> SMS    → Twilio API
    └─> Push   → Firebase FCM
    ↓
Log Delivery Status
    ↓
Store in History
```

---

## 🗄️ Database Schema

### Core Tables

```sql
-- Users (managed by Supabase Auth)
users (
    id UUID PRIMARY KEY,
    email VARCHAR,
    created_at TIMESTAMP
)

-- Student Profiles
student_profiles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    full_name VARCHAR,
    date_of_birth DATE,
    category VARCHAR,
    income_annual INTEGER,
    state VARCHAR,
    district VARCHAR,
    college VARCHAR,
    degree VARCHAR,
    cgpa DECIMAL,
    skills JSONB,
    created_at TIMESTAMP
)

-- Opportunities
opportunities (
    id UUID PRIMARY KEY,
    source VARCHAR,
    category VARCHAR,
    title VARCHAR,
    description TEXT,
    amount_min INTEGER,
    amount_max INTEGER,
    deadline DATE,
    eligibility_rules JSONB,
    documents_required JSONB,
    application_url VARCHAR,
    state_filter JSONB,
    tags JSONB,
    created_at TIMESTAMP
)

-- Applications
applications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    opportunity_id UUID REFERENCES opportunities(id),
    state VARCHAR,
    match_score DECIMAL,
    checklist JSONB,
    progress_pct INTEGER,
    saved BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Notifications
notifications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR,
    body TEXT,
    channel VARCHAR,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
)

-- Notification Preferences
notification_preferences (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    email_enabled BOOLEAN,
    sms_enabled BOOLEAN,
    push_enabled BOOLEAN,
    deadline_reminders BOOLEAN,
    new_matches BOOLEAN,
    status_updates BOOLEAN
)

-- Notification History
notification_history (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    notification_type VARCHAR,
    channel VARCHAR,
    recipient VARCHAR,
    success BOOLEAN,
    error TEXT,
    sent_at TIMESTAMP
)

-- Documents
documents (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    document_type VARCHAR,
    file_path VARCHAR,
    verification_status VARCHAR,
    extracted_fields JSONB,
    confidence_score DECIMAL,
    uploaded_at TIMESTAMP
)

-- Feedback
feedback (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    opportunity_id UUID REFERENCES opportunities(id),
    feedback_type VARCHAR,
    comment TEXT,
    submitted_at TIMESTAMP
)

-- Consent Records
consent_records (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    purpose VARCHAR,
    granted BOOLEAN,
    granted_at TIMESTAMP,
    revoked_at TIMESTAMP
)

-- Audit Logs
audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID,
    action VARCHAR,
    resource VARCHAR,
    details JSONB,
    ip_address VARCHAR,
    timestamp TIMESTAMP
)
```

---

## 🧩 Component Architecture

### Frontend Components

```
app/
├── app/
│   ├── layout.tsx                 # Root layout
│   ├── page.tsx                   # Home page
│   ├── providers.tsx              # Context providers
│   │
│   ├── auth/                      # Authentication
│   │   ├── login/page.tsx
│   │   ├── signup/page.tsx
│   │   └── callback/route.ts
│   │
│   ├── dashboard/                 # Dashboard routes
│   │   ├── layout.tsx             # Dashboard layout
│   │   ├── page.tsx               # Dashboard home
│   │   ├── profile/page.tsx
│   │   ├── scholarships/page.tsx
│   │   ├── notifications/page.tsx
│   │   └── admin/page.tsx
│   │
│   ├── components/                # Reusable components
│   │   ├── Navbar.tsx
│   │   ├── Footer.tsx
│   │   ├── dashboard/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── DashboardHeader.tsx
│   │   │   ├── ProfileForm.tsx
│   │   │   ├── NotificationPrefs.tsx
│   │   │   └── ScholarshipsClient.tsx
│   │   └── home/
│   │       ├── FeaturesSection.tsx
│   │       ├── HowItWorksSection.tsx
│   │       └── FAQsSection.tsx
│   │
│   ├── api/                       # API routes
│   │   └── chat/route.ts          # RAG chatbot API
│   │
│   └── lib/                       # Utilities
│       ├── api.ts                 # API client
│       ├── rag/
│       │   └── vectorStore.ts     # RAG implementation
│       └── supabase/
│           ├── client.ts          # Client-side
│           └── server.ts          # Server-side
```

### Backend Services

```
services/app/
├── main.py                        # FastAPI app
├── config.py                      # Configuration
├── tasks.py                       # Celery tasks
│
├── api/                           # API layer
│   ├── deps.py                    # Dependencies
│   ├── middleware/                # Middleware
│   └── routes/                    # Route handlers
│       ├── scholarships.py
│       ├── profile.py
│       ├── notifications.py
│       ├── search.py
│       ├── documents.py
│       ├── feedback.py
│       ├── consent.py
│       └── admin.py
│
├── db/                            # Database
│   ├── models.py                  # SQLAlchemy models
│   ├── session.py                 # DB session
│   └── migrations/                # Alembic
│
├── intelligence/                  # AI/ML services
│   ├── eligibility.py             # Matching engine
│   ├── embeddings.py              # Vector embeddings
│   ├── recommendation.py          # ML recommendations
│   └── vector_search.py           # Semantic search
│
├── knowledge/                     # Knowledge base
│   └── hybrid_rag.py              # RAG implementation
│
├── notifications/                 # Notification services
│   ├── service.py                 # Base service
│   ├── orchestrator.py            # Multi-channel
│   ├── email.py                   # SendGrid
│   ├── sms.py                     # Twilio
│   ├── push.py                    # Firebase
│   └── deadline_monitor.py        # Cron jobs
│
├── verification/                  # Document verification
│   ├── engine.py                  # Verification engine
│   ├── ocr_service.py             # OCR processing
│   ├── gov_api.py                 # Govt APIs
│   └── parsers.py                 # Document parsers
│
├── security/                      # Security services
│   ├── consent.py                 # Consent management
│   ├── document_store.py          # Encrypted storage
│   ├── rbac.py                    # Access control
│   └── tee.py                     # Trusted execution
│
├── ingestion/                     # Data pipelines
│   ├── base.py                    # Base connector
│   ├── connectors.py              # Connector registry
│   ├── pipeline.py                # ETL pipeline
│   ├── normalizer.py              # Data normalization
│   └── connectors/                # Specific connectors
│       ├── myscheme_connector.py
│       ├── nsp_connector.py
│       └── state_connectors.py
│
├── analytics/                     # Analytics
│   ├── event_service.py           # Event tracking
│   ├── experiment_service.py      # A/B testing
│   └── metrics_calculator.py      # KPI calculation
│
├── workflow/                      # Workflow engine
│   └── engine.py                  # State machine
│
└── agents/                        # AI agents
    ├── chatbot.py                 # Conversational AI
    └── scholarship.py             # Scholarship assistant
```

---

## 🔐 Security Architecture

### Authentication Flow

```
User Login Request
    ↓
Supabase Auth
    ↓
JWT Token Generated
    ↓
Token Stored (HttpOnly Cookie)
    ↓
Include in API Requests
    ↓
Backend Validates Token
    ↓
Extract User Context
    ↓
Check RBAC Permissions
    ↓
Process Request
```

### Authorization Layers

1. **Authentication** - Supabase JWT tokens
2. **API Gateway** - Rate limiting, CORS
3. **RBAC** - Role-based access control
4. **Row-Level Security** - Supabase RLS policies
5. **Data Encryption** - At rest and in transit
6. **Audit Logging** - All sensitive operations

---

## 🚀 Deployment Architecture

### Production Setup

```
┌─────────────────────────────────────────────┐
│          Load Balancer (Cloudflare)         │
└──────────────┬──────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
┌───────▼──────┐  ┌──▼────────────┐
│   Frontend   │  │    Backend    │
│   (Vercel)   │  │  (Railway)    │
│              │  │               │
│  - Next.js   │  │  - FastAPI    │
│  - CDN       │  │  - Uvicorn    │
│  - Edge      │  │  - Workers    │
└──────┬───────┘  └───┬───────────┘
       │              │
       │     ┌────────┴────────┐
       │     │                 │
    ┌──▼─────▼──┐   ┌─────────▼──────┐
    │  Supabase │   │   PostgreSQL   │
    │           │   │   (Managed)    │
    │  - Auth   │   │                │
    │  - Storage│   │   - Primary DB │
    └───────────┘   └────────────────┘
                            │
              ┌─────────────┴────────┐
              │                      │
       ┌──────▼──────┐    ┌─────────▼────┐
       │   ChromaDB  │    │    Redis     │
       │  (Vectors)  │    │   (Cache)    │
       └─────────────┘    └──────────────┘
```

---

## 📊 Performance Considerations

### Frontend Optimization
- Server-side rendering (SSR)
- Static generation for landing pages
- Image optimization (Next.js Image)
- Code splitting
- Lazy loading components
- CDN for static assets

### Backend Optimization
- Database connection pooling
- Redis caching
- Query optimization
- Async/await for I/O operations
- Background tasks (Celery)
- API response compression

### Database Optimization
- Proper indexing
- Query optimization
- Connection pooling
- Read replicas
- Materialized views
- Partitioning large tables

---

## 🔍 Monitoring & Observability

### Metrics to Track
- API response times
- Database query performance
- Error rates
- User engagement
- Notification delivery rates
- LLM response times

### Logging Strategy
- Application logs (Winston/Python logging)
- Access logs (Nginx)
- Database query logs
- Audit logs (user actions)
- Error tracking (Sentry)

### Health Checks
- Frontend: `/health`
- Backend: `/health`
- Database: Connection test
- Redis: Ping test
- External services: Status checks

---

**This architecture is designed for scalability, security, and maintainability.** 🚀
