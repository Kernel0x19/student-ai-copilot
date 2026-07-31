-- Database Migration: pgvector Extension and Performance Indexing
-- Satisfies Requirements: 15.1, 16.1, 16.2, 16.4, 16.5, 16.6, 16.7

-- 1. Enable pgvector extension for PostgreSQL semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Add vector column for opportunity embeddings (384 dimensions)
ALTER TABLE opportunities 
ADD COLUMN IF NOT EXISTS embedding vector(384);

-- 3. Add performance indexes for frequently queried columns (Req 16.1)
CREATE INDEX IF NOT EXISTS idx_opportunities_deadline ON opportunities(deadline);
CREATE INDEX IF NOT EXISTS idx_opportunities_category ON opportunities(category);
CREATE INDEX IF NOT EXISTS idx_opportunities_created_at ON opportunities(created_at);

-- 4. Composite index on (user_id, application_state) for fast user dashboard filtering (Req 16.2)
CREATE INDEX IF NOT EXISTS idx_applications_user_state ON applications(user_id, state);

-- 5. Indexes for fast audit log & event querying
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_action ON audit_logs(user_id, action);
CREATE INDEX IF NOT EXISTS idx_user_events_session ON user_events(session_id);

-- 6. Cosine distance index for fast pgvector retrieval
CREATE INDEX IF NOT EXISTS idx_opportunities_embedding_cosine ON opportunities 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
