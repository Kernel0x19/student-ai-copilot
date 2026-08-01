-- Migration: Add user_events table for analytics event tracking
-- Requirements: 20.1, 20.2, 20.3, 21.1, 21.2
-- Date: 2024

-- Create user_events table
CREATE TABLE IF NOT EXISTS user_events (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    opportunity_id VARCHAR(36),
    application_id VARCHAR(36),
    experiment_name VARCHAR(128),
    variant_name VARCHAR(64),
    match_score FLOAT,
    event_metadata JSON,
    session_id VARCHAR(128),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_user_events_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_events_opportunity FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_events_application FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_user_events_user_id ON user_events(user_id);
CREATE INDEX IF NOT EXISTS idx_user_events_event_type ON user_events(event_type);
CREATE INDEX IF NOT EXISTS idx_user_events_opportunity_id ON user_events(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_user_events_created_at ON user_events(created_at);
CREATE INDEX IF NOT EXISTS idx_user_events_experiment_name ON user_events(experiment_name);
CREATE INDEX IF NOT EXISTS idx_user_events_variant_name ON user_events(variant_name);
CREATE INDEX IF NOT EXISTS idx_user_events_session_id ON user_events(session_id);

-- Composite index for experiment analysis queries
CREATE INDEX IF NOT EXISTS idx_user_events_experiment_analysis 
ON user_events(experiment_name, variant_name, event_type, created_at);

-- Composite index for user activity analysis
CREATE INDEX IF NOT EXISTS idx_user_events_user_activity 
ON user_events(user_id, created_at DESC);

COMMIT;
