# cdp/demo_campaigner.py
import argparse, smtplib, json, random
from email.message import EmailMessage
from email.utils import formataddr
from .db import get_conn, q
from .utils import corr_id, log
from .config import settings

def render_tpl(tpl_html: str, **kw) -> str:
    out = tpl_html
    for k, v in kw.items():
        out = out.replace("{{"+k+"}}", str(v))
    return out

def load_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def send_html(to_addr: str, subject: str, html: str):
    msg = EmailMessage()
    msg["From"] = formataddr(("CDP Mailer", settings.from_addr))
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content("Your email client does not support HTML.")
    msg.add_alternative(html, subtype="html")
    smtp = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15)
    if settings.smtp_user and settings.smtp_pass:
        try: smtp.starttls()
        except Exception: pass
        smtp.login(settings.smtp_user, settings.smtp_pass)
    smtp.send_message(msg)
    try: smtp.quit()
    except Exception: pass

def choose_one(candidates, strategy: str):
    if not candidates:
        return None
    if strategy == "random":
        return random.choice(candidates)
    # highest risk: max by score (fallback to newest later)
    if "score" in candidates[0]:
        return max(candidates, key=lambda r: float(r["score"]))
    # newest: max by as_of_ts
    return max(candidates, key=lambda r: r.get("as_of_ts") or "")

def main():
    ap = argparse.ArgumentParser(
        description="Demo sender: send ONE email per run to a real inbox using miss-you or good-activity template."
    )
    ap.add_argument("--recipient", required=True, help="Your real inbox (Mailgun sandbox-safe).")
    ap.add_argument("--miss-template", required=True, help="Path to miss_you.html")
    ap.add_argument("--good-template", required=True, help="Path to good_activity.html")
    ap.add_argument("--to-domain", default="example.com", help="Synthetic intended domain for display.")
    ap.add_argument("--segment", choices=["auto","miss","good"], default="auto",
                    help="Force which template to use, or auto by rules.")
    ap.add_argument("--user", help="Target a specific user_id (overrides auto selection).")
    ap.add_argument("--strategy", choices=["highest","random","newest"], default="highest",
                    help="When auto-selecting, how to pick one user.")
    ap.add_argument("--high-threshold", type=float, default=0.70)
    ap.add_argument("--good-max-score", type=float, default=0.50)
    ap.add_argument("--good-min-logins", type=int, default=7)
    ap.add_argument("--min-inactivity", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    miss_tpl = load_file(args.miss_template)
    good_tpl = load_file(args.good_template)

    cid = corr_id()
    chosen = None
    chosen_campaign = None

    with get_conn() as conn:
        rows = q(conn, "SELECT user_id, as_of_ts, score, features FROM current_scores") or []

        # Build features and segments
        enriched = []
        for r in rows:
            feats = r["features"] or {}
            enriched.append({
                "user_id": r["user_id"],
                "as_of_ts": r["as_of_ts"],
                "score": float(r["score"]),
                "inactivity_days": float(feats.get("inactivity_days", 0) or 0),
                "logins_window": int(feats.get("logins_window", 0) or 0),
                "purchases_window": int(feats.get("purchases_window", 0) or 0),
            })

        # If specific user requested
        if args.user:
            one = next((x for x in enriched if x["user_id"] == args.user), None)
            if not one:
                log("email", "demo_campaigner", correlation_id=cid, status="no_user", user_id=args.user)
                print(f"No current score for user_id={args.user}")
                return
            # Decide campaign for this user
            if args.segment in ("miss","auto"):
                if one["score"] >= args.high_threshold or one["inactivity_days"] >= args.min_inactivity:
                    chosen = one; chosen_campaign = "churn-offer-1"
                elif args.segment == "miss":
                    print(f"User {args.user} does not meet miss-you criteria.")
                    return
            if not chosen and args.segment in ("good","auto"):
                if one["score"] < args.good_max_score and (one["logins_window"] >= args.good_min_logins or one["purchases_window"] >= 1):
                    chosen = one; chosen_campaign = "loyalty-thanks-1"
                elif args.segment == "good":
                    print(f"User {args.user} does not meet good-activity criteria.")
                    return
        else:
            # Auto-select one candidate by segment
            miss = [x for x in enriched if x["score"] >= args.high_threshold or x["inactivity_days"] >= args.min_inactivity]
            good = [x for x in enriched if x["score"] < args.good_max_score and (x["logins_window"] >= args.good_min_logins or x["purchases_window"] >= 1)]

            # If segment forced, use that list; else prefer miss, then good
            pool = miss if args.segment in ("miss","auto") and miss else []
            if not pool and args.segment in ("good","auto"):
                pool = good
            if pool:
                chosen = choose_one(pool, args.strategy)
                chosen_campaign = "churn-offer-1" if chosen in miss else "loyalty-thanks-1"

        if not chosen:
            print("No qualifying user found for the selected segment/rules.")
            log("email", "demo_campaigner", correlation_id=cid, status="no_candidate")
            return

        uid = chosen["user_id"]
        intended_to = f"{uid}@{args.to_domain}"

        if chosen_campaign == "churn-offer-1":
            subject = f"[CDP] We miss you: {uid}"
            html = render_tpl(miss_tpl,
                              user_id=uid,
                              inactivity_days=chosen["inactivity_days"],
                              logins_window=chosen["logins_window"],
                              purchases_window=chosen["purchases_window"],
                              intended_to=intended_to)
        else:
            subject = f"[CDP] Thank you: {uid}"
            html = render_tpl(good_tpl,
                              user_id=uid,
                              inactivity_days=chosen["inactivity_days"],
                              logins_window=chosen["logins_window"],
                              purchases_window=chosen["purchases_window"],
                              intended_to=intended_to)

        status = "skipped" if args.dry_run else "sent"
        error = None
        try:
            if not args.dry_run:
                send_html(args.recipient, subject, html)
        except Exception as e:
            status = "failed"
            error = str(e)

        # Audit row (alert_id is NULL since this is score-based)
        q(conn, "INSERT INTO notifications_log(alert_id, user_id, campaign_id, status, error) VALUES (NULL,%s,%s,%s,%s)",
          (uid, chosen_campaign, status, error))
        log("email", "demo_campaigner", correlation_id=cid, user_id=uid, campaign_id=chosen_campaign,
            status=status, intended_to=intended_to, to_addr=args.recipient, segment=("miss" if chosen_campaign=="churn-offer-1" else "good"))
        print(f"{status.upper()}: {uid} -> {args.recipient} ({'miss-you' if chosen_campaign=='churn-offer-1' else 'good-activity'})")

if __name__ == "__main__":
    main()
