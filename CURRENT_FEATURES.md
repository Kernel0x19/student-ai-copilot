# 🎓 EduPilot Platform - Current Features Documentation

**Last Updated:** August 4, 2026  
**Version:** 1.0.0  
**Platform:** EduPilot - AI-Powered Student Assistant Platform

---

## 📋 Table of Contents

- [Platform Overview](#platform-overview)
- [Core Features](#core-features)
- [Feature Details by Module](#feature-details-by-module)
- [Data Connectors](#data-connectors)
- [API Endpoints](#api-endpoints)
- [External Integrations](#external-integrations)
- [Technology Stack](#technology-stack)

---

## 🌟 Platform Overview

**EduPilot** is a comprehensive AI-powered platform designed to help students discover, track, and apply for educational opportunities including scholarships, internships, and skill development programs. The platform currently serves **788+ student schemes** across various categories and states in India.

### Key Statistics
- **Total Opportunities:** 788+ student schemes
- **Categories:** Scholarships, Internships, Grants, Skill Development, Financial Assistance
- **Coverage:** All Indian states
- **Government Departments:** 20+ ministries
- **Active Connectors:** AICTE, Unstop, Internshala

---

## 🚀 Core Features

### 1. **AI-Powered Chatbot (RAG System)**
- **Description:** Natural language conversational interface for querying student schemes
- **Technology:** LangChain + Ollama (gpt-oss:120b-cloud model)
- **Knowledge Base:** 788+ student schemes indexed in ChromaDB
- **Capabilities:**
  - Answer questions about scholarships, internships, and schemes
  - Semantic search through all opportunities
  - Context-aware responses with source citations
  - Real-time query processing
- **Files:** 
  - Frontend: `app/ai-chat/page.tsx`
  - Backend: `services/app/agents/chatbot.py`
  - API: `app/api/chat/route.ts`

### 2. **Semantic Search Engine**
- **Description:** Intelligent search using vector embeddings for natural language queries
- **Technology:** ChromaDB + Sentence Transformers
- **Features:**
  - Natural language query understanding
  - Category filtering (scholarship, internship, grant, etc.)
  - Relevance scoring and ranking
  - Fast vector similarity search
  - Top-K retrieval with configurable results
- **Files:** `services/app/intelligence/vector_search.py`

### 3. **Smart Eligibility Matching**
- **Description:** Automatic eligibility checking based on student profile
- **Matching Criteria:**
  - Academic qualifications (degree, CGPA, percentage)
  - Income criteria (family income verification)
  - Category (SC/ST/OBC/EWS/General)
  - State/location requirements
  - Age limits and restrictions
  - Course/degree type
  - Stream/specialization
- **Features:**
  - Real-time eligibility scoring (0.0 - 1.0)
  - Detailed reason explanations
  - Multi-criteria matching
  - Rule-based engine with fuzzy matching
- **Files:** `services/app/intelligence/eligibility.py`

### 4. **Multi-Channel Notification System** ✅
- **Description:** Comprehensive notification delivery across multiple channels
- **Channels Supported:**
  - **In-App Notifications** - Database-stored, real-time dashboard alerts
  - **Email** - Via SendGrid API (100 emails/day free tier)
  - **SMS** - Via Twilio API (for urgent deadlines)
  - **Push Notifications** - Via Firebase Cloud Messaging (browser/mobile)
- **Notification Types:**
  - Deadline reminders (7-day advance, 2-day urgent)
  - New opportunity matches
  - Application status updates
  - Deadline change alerts
  - Document verification status
- **User Controls:**
  - Toggle each channel on/off per user
  - Configure notification types preferences
  - Quiet hours support
  - Priority-based delivery
- **Files:** 
  - `services/app/notifications/` (complete module)
  - `services/app/notifications/orchestrator.py`
  - `NOTIFICATION_GUIDE.md`

### 5. **Document Upload & OCR System**
- **Description:** Secure document management with automatic data extraction
- **Supported Documents:**
  - Aadhaar Card
  - PAN Card
  - Income Certificate
  - Caste Certificate
  - Educational Certificates (10th, 12th, Degree)
  - Bank Statements
  - Domicile Certificate
- **Features:**
  - OCR text extraction (Tesseract)
  - Field validation and parsing
  - Encrypted document storage
  - Government API verification (optional)
  - Document type auto-detection
  - Data extraction with confidence scores
- **Files:** 
  - `services/app/verification/ocr_service.py`
  - `services/app/verification/parsers.py`
  - `services/app/security/document_store.py`

### 6. **Student Profile Management**
- **Description:** Comprehensive student profile with verification
- **Profile Fields:**
  - Personal Information (name, DOB, contact)
  - Academic Details (degree, CGPA, institution)
  - Financial Information (family income)
  - Category Information (SC/ST/OBC/General)
  - Location (state, district, city)
  - Documents uploaded
  - Preferences and interests
- **Features:**
  - Profile completion tracking
  - Document verification status
  - Privacy consent management
  - Data encryption at rest
- **Files:** `services/app/api/routes/profile.py`

### 7. **Application Workflow Engine**
- **Description:** State machine for tracking application progress
- **Application States:**
  1. `DISCOVERED` - Opportunity found and saved
  2. `ELIGIBILITY_CHECK` - Checking student eligibility
  3. `DOCUMENT_VALIDATION` - Verifying required documents
  4. `HUMAN_REVIEW` - Manual review by student
  5. `SUBMITTED` - Application submitted to portal
  6. `IN_PROGRESS` - Application under review
  7. `ACCEPTED` - Application accepted
  8. `REJECTED` - Application rejected
  9. `WITHDRAWN` - Student withdrew application
- **Features:**
  - State transition validation
  - Workflow automation
  - Progress tracking
  - Timeline history
- **Files:** `services/app/workflow/engine.py`

### 8. **Admin Analytics Dashboard** ✅
- **Description:** Platform monitoring and analytics for administrators
- **Metrics Tracked:**
  - User engagement (DAU, MAU, retention)
  - Opportunity discovery rates
  - Application conversion funnel
  - Document verification rates
  - Notification delivery stats
  - Connector health and data freshness
  - API performance metrics
- **Features:**
  - Real-time platform KPIs
  - Data quality monitoring
  - Connector status dashboard
  - A/B experiment tracking
  - User feedback analytics
  - Audit logs and compliance
- **Files:** 
  - `services/app/api/routes/admin.py`
  - `services/app/analytics/`
  - `app/app/dashboard/admin/page.tsx`

### 9. **Security & Privacy Features** ✅
- **Description:** Comprehensive security and privacy controls
- **Authentication:**
  - Supabase Auth integration
  - Email/password authentication
  - Social login (Google, GitHub)
  - Session management
  - Role-based access control (RBAC)
- **Privacy Features:**
  - GDPR-compliant consent management
  - User data access controls
  - Right to be forgotten
  - Data export functionality
  - Privacy policy acknowledgment
- **Security Measures:**
  - Document encryption at rest
  - Secure API endpoints
  - Audit logging for all data access
  - Rate limiting
  - Input validation and sanitization
- **Files:** 
  - `services/app/security/`
  - `services/app/security/consent.py`
  - `services/app/security/rbac.py`
  - `services/app/security/tee.py`

### 10. **A/B Testing & Experimentation Framework**
- **Description:** Built-in experimentation framework for feature testing
- **Features:**
  - User variant assignment
  - Experiment context middleware
  - Metrics tracking per variant
  - Statistical significance testing
  - Experiment lifecycle management
- **Capabilities:**
  - Create and manage experiments
  - Automatic user assignment to variants
  - Track conversion metrics
  - Compare variant performance
  - Gradual rollout support
- **Files:** 
  - `services/app/analytics/experiment_service.py`
  - `services/app/api/middleware/ExperimentContextMiddleware`
  - `services/app/api/routes/experiments.py`

---

## 📊 Feature Details by Module

### Frontend Features (Next.js App)

#### Landing Page Components
- **Hero Section** - Value proposition and CTA
- **Features Section** - Platform capabilities showcase
- **Benefits Section** - Student value highlights
- **How It Works** - Step-by-step workflow
- **FAQ Section** - Common questions
- **Terminal Card** - Interactive demo

#### Dashboard Components
- **Main Dashboard** - Overview of opportunities
- **Profile Page** - Student profile management
- **Scholarships Page** - Browse and search scholarships
- **Internships Page** - Browse internship opportunities
- **Documents Page** - Upload and manage documents
- **Search Page** - Advanced semantic search
- **Chat Page** - AI chatbot interface
- **Notifications Page** - Notification center
- **Consent Page** - Privacy preferences
- **Admin Page** - Platform analytics (admin only)

#### Navigation & Layout
- **Responsive Navbar** - Mobile-friendly navigation
- **Sidebar** - Dashboard navigation menu
- **Footer** - Links and information
- **Auth Pages** - Login and signup flows

### Backend Features (FastAPI Services)

#### Agents Module
- **Chatbot Agent** (`agents/chatbot.py`)
  - LangChain-based conversational AI
  - Context-aware responses
  - Source citation
  
- **Scholarship Agent** (`agents/scholarship.py`)
  - Opportunity recommendation
  - Eligibility matching
  - Application assistance

- **Document Identifier** (`agents/document_identifier.py`)
  - Document type classification
  - Field extraction guidance

#### Intelligence Module
- **Eligibility Engine** (`intelligence/eligibility.py`)
  - Rule-based matching
  - Fuzzy criteria matching
  - Scoring algorithm

- **Embeddings Service** (`intelligence/embeddings.py`)
  - Text vectorization
  - Sentence transformers integration
  - Batch processing

- **Recommendation Engine** (`intelligence/recommendation.py`)
  - ML-based opportunity ranking
  - Personalized suggestions
  - Collaborative filtering

- **Vector Search** (`intelligence/vector_search.py`)
  - Semantic similarity search
  - Fast retrieval
  - Category filtering

#### Notification Module
- **Service Base** (`notifications/service.py`)
  - Abstract notification service
  - Retry logic
  - Error handling

- **Orchestrator** (`notifications/orchestrator.py`)
  - Multi-channel coordination
  - Priority management
  - Fallback handling

- **Email Service** (`notifications/email.py`)
  - SendGrid integration
  - Template support
  - Delivery tracking

- **SMS Service** (`notifications/sms.py`)
  - Twilio integration
  - Character limits
  - Cost optimization

- **Push Service** (`notifications/push.py`)
  - Firebase FCM integration
  - Device token management
  - Rich notifications

- **Deadline Monitor** (`notifications/deadline_monitor.py`)
  - Automatic deadline tracking
  - Scheduled reminders
  - Celery task integration

#### Verification Module
- **Engine** (`verification/engine.py`)
  - Verification workflow coordination
  - Status tracking
  - Result aggregation

- **OCR Service** (`verification/ocr_service.py`)
  - Tesseract integration
  - Image preprocessing
  - Text extraction

- **Government API** (`verification/gov_api.py`)
  - DigiLocker integration
  - Aadhaar verification
  - API retry logic

- **Parsers** (`verification/parsers.py`)
  - Document-specific field extraction
  - Pattern matching
  - Data normalization

#### Security Module
- **Consent Manager** (`security/consent.py`)
  - GDPR compliance
  - Consent tracking
  - Withdrawal handling

- **Document Store** (`security/document_store.py`)
  - Encrypted storage
  - Access logging
  - Secure retrieval

- **RBAC** (`security/rbac.py`)
  - Role definitions
  - Permission checking
  - Access control

- **TEE (Trusted Execution)** (`security/tee.py`)
  - Secure computation
  - Mock implementation
  - Production stubs

---

## 🔌 Data Connectors

### Overview
Data connectors automatically fetch opportunities from external sources. The platform uses a **connector orchestrator** that manages execution, error handling, and data normalization.

### Active Connectors

#### 1. AICTE Connector ✅
- **Source:** All India Council for Technical Education
- **Type:** Web Scraper (Playwright-based)
- **Category:** Scholarships, Grants, Fellowships
- **Technology:** 
  - Playwright browser automation
  - BeautifulSoup HTML parsing
  - Anti-bot detection measures
- **Features:**
  - Real browser simulation
  - JavaScript execution
  - Realistic fingerprints
  - Rate limiting (2s delay)
- **Data Extracted:**
  - Title, description
  - Amount (min/max)
  - Deadline
  - Eligibility criteria
  - Application URL
- **Files:** `services/app/ingestion/connectors/aicte.py`
- **Status:** ✅ Active and working

#### 2. Unstop Connector ✅
- **Source:** Unstop (formerly Dare2Compete)
- **Type:** API-based (with web scraping fallback)
- **Category:** Competitions, Hackathons, Challenges
- **Technology:**
  - REST API integration
  - Playwright fallback
  - Rate limiting
- **Features:**
  - API-first approach
  - Automatic fallback to scraping
  - Data normalization
  - Rate limiting (2s delay)
- **Data Extracted:**
  - Competition details
  - Prize money
  - Deadlines
  - Registration links
  - Eligibility criteria
- **Files:** `services/app/ingestion/connectors/unstop.py`
- **Status:** ✅ Active and working

#### 3. Internshala Connector ✅
- **Source:** Internshala
- **Type:** Web Scraper (Playwright-based)
- **Category:** Internships
- **Technology:**
  - Playwright browser automation
  - robots.txt compliance checking
  - User-agent rotation
  - Comprehensive activity logging
- **Features:**
  - Robots.txt validation
  - Rate limiting (3s delay)
  - User-agent rotation (4 variants)
  - Audit logging for compliance
  - Error isolation
- **Data Extracted:**
  - Title, company
  - Location, duration
  - Stipend information
  - Deadline
  - Application URL
  - Eligibility criteria
- **Files:** `services/app/ingestion/connectors/internshala.py`
- **Status:** ✅ Active and working

### Connector Infrastructure

#### Connector Orchestrator
- **Description:** Central manager for all connectors
- **Features:**
  - Sequential connector execution
  - Error isolation (failed connectors don't block others)
  - Database integration
  - Deadline change detection
  - Status tracking and monitoring
  - Execution logging
- **Capabilities:**
  - Run all connectors in sequence
  - Run individual connector by name
  - Health checks
  - Performance metrics
- **Files:** 
  - `services/app/ingestion/connector_registry.py`
  - `services/app/ingestion/pipeline.py`

#### Data Normalization
- **Description:** Standardizes data from different sources
- **Process:**
  1. Extract raw data from source
  2. Parse HTML/JSON into structured format
  3. Normalize fields to standard schema
  4. Validate and clean data
  5. Store in database
- **Schema Fields:**
  - `title`, `description`
  - `amount_min`, `amount_max`, `amount`
  - `deadline`, `duration`
  - `eligibility_rules` (JSON)
  - `source_url`, `application_url`
  - `source`, `category`
  - `tags`, `state_filter`
  - `documents_required`
- **Files:** `services/app/ingestion/normalizer.py`

#### Connector Features

**Deduplication:**
- Checks for existing opportunities by `source_url`
- Updates existing records instead of creating duplicates
- Preserves user-facing IDs

**Deadline Change Detection:**
- Monitors deadline changes for opportunities
- Creates audit log entries
- Identifies affected students with active applications
- Triggers notifications automatically

**Status Tracking:**
- `last_run` - Timestamp of last execution
- `last_success` - Timestamp of last successful run
- `last_error` - Error message if failed
- `records_processed` - Count of records fetched
- `is_stale` - Flag for monitoring alerts

**Rate Limiting:**
- Configurable delays between requests
- Prevents IP banning
- Respects source server resources

**Error Handling:**
- Try-catch for each connector
- Continue execution on failure (error isolation)
- Detailed error logging with context
- Diagnostic information for debugging

---

## 🔗 API Endpoints

### Base URL
- **Production:** `https://api.edupilot.com` (if deployed)
- **Development:** `http://localhost:8000`

### Authentication
- **Method:** Supabase JWT tokens
- **Header:** `Authorization: Bearer <token>`

### Available Endpoints

#### Scholarships
- `GET /api/v1/scholarships` - List all scholarships
- `GET /api/v1/scholarships/{id}` - Get scholarship details
- `POST /api/v1/scholarships/search` - Semantic search
- `GET /api/v1/scholarships/recommended` - Personalized recommendations

#### Profile
- `GET /api/v1/profile` - Get user profile
- `PUT /api/v1/profile` - Update user profile
- `POST /api/v1/profile/documents` - Upload document
- `GET /api/v1/profile/documents` - List uploaded documents

#### Consent
- `GET /api/v1/consent` - Get consent status
- `POST /api/v1/consent` - Update consent preferences
- `GET /api/v1/consent/history` - Consent history

#### Notifications
- `GET /api/v1/notifications` - List notifications
- `PUT /api/v1/notifications/{id}/read` - Mark as read
- `POST /api/v1/notifications/preferences` - Update preferences
- `GET /api/v1/notifications/preferences` - Get preferences

#### Workflow
- `GET /api/v1/workflow/applications` - List applications
- `POST /api/v1/workflow/applications` - Create application
- `PUT /api/v1/workflow/applications/{id}` - Update application state
- `GET /api/v1/workflow/applications/{id}/history` - Application timeline

#### Admin
- `GET /api/v1/admin/metrics` - Platform metrics
- `GET /api/v1/admin/connectors` - Connector status
- `POST /api/v1/admin/connectors/{name}/run` - Trigger connector
- `GET /api/v1/admin/users` - List users (admin only)
- `GET /api/v1/admin/audit-logs` - Audit logs

#### Search
- `POST /api/v1/search/semantic` - Semantic search
- `GET /api/v1/search/opportunities` - Filter opportunities
- `POST /api/v1/search/suggest` - Auto-suggestions

#### Documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/{id}` - Get document
- `POST /api/v1/documents/{id}/verify` - Trigger verification
- `GET /api/v1/documents/{id}/status` - Verification status

#### Connectors
- `GET /api/v1/connectors` - List available connectors
- `GET /api/v1/connectors/{name}/status` - Connector health
- `POST /api/v1/connectors/{name}/trigger` - Manual trigger

#### Chat
- `POST /api/v1/chat` - Send chat message to AI
- `GET /api/v1/chat/history` - Chat history
- `DELETE /api/v1/chat/history` - Clear chat history

#### Experiments
- `GET /api/v1/experiments` - List experiments
- `POST /api/v1/experiments` - Create experiment
- `GET /api/v1/experiments/{id}/results` - Experiment results

#### Feedback
- `POST /api/v1/feedback` - Submit feedback
- `GET /api/v1/feedback` - List feedback (admin)

### API Documentation
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

## 🌐 External Integrations

### 1. Supabase
- **Purpose:** Authentication & Database (alternative)
- **Features Used:**
  - Auth (email/password, social login)
  - User management
  - Session handling
- **Integration:** `app/app/lib/supabase/`
- **Free Tier:** 500MB database, unlimited auth

### 2. SendGrid
- **Purpose:** Email notifications
- **Features Used:**
  - Transactional emails
  - Template support
  - Delivery tracking
- **Integration:** `services/app/notifications/email.py`
- **Free Tier:** 100 emails/day
- **Status:** ✅ Configured (API key required)

### 3. Twilio
- **Purpose:** SMS notifications
- **Features Used:**
  - SMS sending
  - Delivery status
  - Error handling
- **Integration:** `services/app/notifications/sms.py`
- **Free Tier:** $15 trial credit
- **Status:** ✅ Configured (credentials in .env)

