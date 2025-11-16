-- ===============================================
-- CDP Prototype - Phase 2: Seed users (+ tiny sample events)
-- ===============================================

-- Create 200 users distributed over last 60 days
WITH u AS (
  SELECT 'user_'||to_char(i,'FM000') AS user_id,
         now() - ((random()*60)::int || ' days')::interval AS signup_ts
  FROM generate_series(1,200) AS g(i)
)
INSERT INTO users(user_id, signup_ts, attrs)
SELECT user_id, signup_ts, jsonb_build_object(
  'plan', (ARRAY['free','pro','enterprise'])[1 + floor(random()*3)::int],
  'country', (ARRAY['IN','US','TR','DE','GB'])[1 + floor(random()*5)::int]
)
FROM u
ON CONFLICT (user_id) DO NOTHING;

-- A couple of illustrative users with simple events (for quick smoke tests)
-- user_999 and user_998 are special demo IDs
INSERT INTO users(user_id, signup_ts) VALUES
('user_999', now() - interval '20 days'),
('user_998', now() - interval '20 days')
ON CONFLICT (user_id) DO NOTHING;

-- user_999: active (login every ~2 days, plus one purchase)
WITH d AS (
  SELECT generate_series(now() - interval '14 days', now(), interval '2 days') AS ts
)
INSERT INTO events(user_id, ts, event_type, properties)
SELECT 'user_999', ts, 'login', '{}'::jsonb FROM d;
INSERT INTO events(user_id, ts, event_type, properties)
VALUES ('user_999', now() - interval '3 days', 'purchase', jsonb_build_object('amount', 49));

-- user_998: inactive (no login for > 7 days)
WITH d AS (
  SELECT generate_series(now() - interval '14 days', now() - interval '8 days', interval '3 days') AS ts
)
INSERT INTO events(user_id, ts, event_type, properties)
SELECT 'user_998', ts, 'login', '{}'::jsonb FROM d;

-- Done
