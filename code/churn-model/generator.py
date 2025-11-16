import argparse, random
from datetime import timedelta
from .db import get_conn, q, execmany
from .utils import now_utc, corr_id, log

def generate_events(users, days, inactive_rate, seed):
    rng = random.Random(seed)
    start = now_utc() - timedelta(days=days)
    end = now_utc()
    rows = []
    # Fetch users list if not provided explicitly
    with get_conn() as conn:
        all_users = [r['user_id'] for r in q(conn, "SELECT user_id FROM users ORDER BY user_id")]
    if users and users != ["ALL"]:
        target = [u for u in all_users if u in users]
    else:
        target = all_users
    # Assign some users as drifting inactive
    inactive_set = set(rng.sample(target, k=max(1, int(len(target)*inactive_rate))))
    for uid in target:
        # baseline: ~1 login every 2 days
        t = start
        last_login = None
        drift = uid in inactive_set
        while t <= end:
            # probability of login depends on drift
            p = 0.5 if not drift else 0.2
            if rng.random() < p:
                rows.append((uid, t, 'login', '{}'))
                last_login = t
                # occasional purchase for active users
                if not drift and rng.random() < 0.2:
                    rows.append((uid, t, 'purchase', '{"amount": %d}' % rng.randint(10,150)))
            # step ~1 day
            t += timedelta(days=1)
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", default="ALL", help="Comma-separated user_ids or ALL")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--inactive-rate", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    users = ["ALL"] if args.users == "ALL" else [u.strip() for u in args.users.split(",") if u.strip()]
    rows = generate_events(users, args.days, args.inactive_rate, args.seed)
    cid = corr_id()
    with get_conn() as conn:
        if rows:
            execmany(conn, "INSERT INTO events(user_id, ts, event_type, properties) VALUES (%s,%s,%s,%s)", rows)
            conn.commit()
    log("ingest", "simulator", correlation_id=cid, inserted=len(rows), users=len(set([r[0] for r in rows])))

if __name__ == "__main__":
    main()
