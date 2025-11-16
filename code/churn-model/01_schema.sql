-- ===============================================
-- CDP Prototype - Phase 2: Database Schema (Postgres)
-- ===============================================
-- Safe defaults
SET client_min_messages = WARNING;

-- Create tables
CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY,
  signup_ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  attrs JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS events (
  event_id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  ts TIMESTAMPTZ NOT NULL,
  event_type TEXT NOT NULL CHECK (event_type IN ('login','purchase')),
  properties JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_events_user_ts ON events(user_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_events_type_ts ON events(event_type, ts DESC);

CREATE TABLE IF NOT EXISTS churn_scores (
  user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  as_of_ts TIMESTAMPTZ NOT NULL,
  score NUMERIC NOT NULL CHECK (score >= 0 AND score <= 1),
  features JSONB NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY (user_id, as_of_ts)
);

CREATE INDEX IF NOT EXISTS idx_churn_scores_ts ON churn_scores(as_of_ts DESC);

CREATE TABLE IF NOT EXISTS alerts (
  alert_id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  severity TEXT NOT NULL CHECK (severity IN ('high','medium')),
  reason TEXT NOT NULL,
  features JSONB NOT NULL DEFAULT '{}'::jsonb,
  status TEXT NOT NULL CHECK (status IN ('OPEN','NOTIFIED','RESOLVED')) DEFAULT 'OPEN',
  campaign_id TEXT,
  last_updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_notified_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at DESC);

CREATE TABLE IF NOT EXISTS notifications_log (
  id BIGSERIAL PRIMARY KEY,
  alert_id BIGINT NOT NULL REFERENCES alerts(alert_id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  sent_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  campaign_id TEXT,
  status TEXT NOT NULL CHECK (status IN ('sent','skipped','failed')),
  error TEXT
);

-- Convenience view: latest score per user
CREATE OR REPLACE VIEW current_scores AS
SELECT DISTINCT ON (user_id)
  user_id, as_of_ts, score, features
FROM churn_scores
ORDER BY user_id, as_of_ts DESC;

-- Convenience view: current open alert per user (if any)
CREATE OR REPLACE VIEW current_open_alert AS
SELECT DISTINCT ON (user_id)
  user_id, alert_id, severity, reason, status, created_at, last_updated_at
FROM alerts
WHERE status = 'OPEN'
ORDER BY user_id, created_at DESC;

-- Done
