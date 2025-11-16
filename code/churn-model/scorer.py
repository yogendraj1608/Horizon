import argparse
from datetime import timedelta
from statistics import mean
from .db import get_conn, q, execmany
from .utils import now_utc, corr_id, log, moving_avg_days

def compute_features(conn, window_days):
    as_of = now_utc()
    window_start = as_of - timedelta(days=window_days)
    users = q(conn, "SELECT user_id FROM users")
    out = []
    for r in users:
        uid = r['user_id']
        ev = q(conn, "SELECT ts, event_type FROM events WHERE user_id=%s AND ts >= %s ORDER BY ts ASC", (uid, window_start))
        if not ev:
            inactivity_days = window_days
            logins = 0
            purchases = 0
            avg_gap = None
        else:
            ts_list = [e['ts'] for e in ev if e['event_type']=='login']
            logins = len(ts_list)
            purchases = sum(1 for e in ev if e['event_type']=='purchase')
            last_ts = ev[-1]['ts']
            inactivity_days = (as_of - last_ts).total_seconds()/86400.0
            avg_gap = moving_avg_days(ts_list) if len(ts_list) >= 2 else None
        feats = {
            "inactivity_days": round(inactivity_days,2),
            "logins_window": logins,
            "purchases_window": purchases,
            "avg_days_between_logins": round(avg_gap,2) if avg_gap else None
        }
        # Rule-based score (0..1): more inactivity increases score, more logins/purchases decrease it
        base = min(1.0, max(0.0, (inactivity_days / max(1.0, window_days))))
        bonus = 0.0
        if logins >= window_days/2:  # very active
            bonus -= 0.3
        elif logins >= window_days/4:
            bonus -= 0.15
        if purchases >= 2:
            bonus -= 0.2
        score = min(1.0, max(0.0, base + bonus))
        out.append((uid, as_of, score, feats))
    return as_of, out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=14)
    args = ap.parse_args()
    cid = corr_id()
    with get_conn() as conn:
        as_of, rows = compute_features(conn, args.window)
        # upsert churn_scores
        execmany(conn,
            "INSERT INTO churn_scores(user_id, as_of_ts, score, features) VALUES (%s,%s,%s,%s) "
            "ON CONFLICT (user_id, as_of_ts) DO NOTHING",
            [(u, as_of, s, jsonb(feats)) for (u, as_of, s, feats) in rows]
        )
        conn.commit()
    # log
    total = len(rows)
    # summarize histogram-ish buckets
    high = sum(1 for (_,_,s,_) in rows if s >= 0.7)
    med = sum(1 for (_,_,s,_) in rows if 0.5 <= s < 0.7)
    low = total - high - med
    log("score", "scorer", correlation_id=cid, window_days=args.window, users=total, high=high, medium=med, low=low)

# helper to make jsonb literals for psycopg2
def jsonb(obj):
    import json
    return json.dumps(obj)

if __name__ == "__main__":
    main()
