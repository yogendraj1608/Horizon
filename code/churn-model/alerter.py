import argparse
from datetime import timedelta
from .db import get_conn, q
from .utils import now_utc, corr_id, log
from .config import settings

def recent_duplicate(conn, user_id, reason, cooldown_days):
    rows = q(conn, "SELECT 1 FROM alerts WHERE user_id=%s AND reason=%s AND created_at >= now() - (%s || ' days')::interval",
             (user_id, reason, cooldown_days))
    return bool(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--high-threshold", type=float, default=None, help="Override high threshold")
    ap.add_argument("--cooldown-days", type=int, default=None)
    args = ap.parse_args()
    hi = args.high_threshold if args.high_threshold is not None else settings.score_threshold_high
    cooldown = args.cooldown_days if args.cooldown_days is not None else settings.cooldown_days
    cid = corr_id()

    with get_conn() as conn:
        rows = q(conn, "SELECT user_id, score, features FROM current_scores")
        created = 0
        for r in rows:
            uid, score, feats = r['user_id'], float(r['score']), r['features']
            if score >= hi:
                reason = "score_gt_%.2f" % hi
                if recent_duplicate(conn, uid, reason, cooldown):
                    continue
                q(conn, "INSERT INTO alerts(user_id, severity, reason, features, status) VALUES (%s,'high',%s,%s,'OPEN')",
                  (uid, reason, jsonb(feats)))
                created += 1
        conn.commit()
    log("alert", "alerter", correlation_id=cid, created=created, threshold=hi, cooldown_days=cooldown)

def jsonb(obj):
    import json
    return json.dumps(obj)

if __name__ == "__main__":
    main()
