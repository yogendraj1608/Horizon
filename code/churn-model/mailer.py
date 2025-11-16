import argparse, smtplib
from email.message import EmailMessage
from .db import get_conn, q
from .utils import corr_id, log
from .config import settings

def main():
    ap = argparse.ArgumentParser(description="Send ONE aggregated email listing all high-risk users.")
    ap.add_argument("--campaign", default="churn-offer-1", help="Campaign id to record in DB.")
    ap.add_argument("--recipient", required=True, help="The single destination email address (your inbox).")
    ap.add_argument("--dry-run", action="store_true", help="Do not actually send; still update logs/DB as 'skipped'.")
    args = ap.parse_args()

    cid = corr_id()
    with get_conn() as conn:
        alerts = q(conn, "SELECT alert_id, user_id FROM alerts WHERE status='OPEN' AND severity='high'")
        user_ids = [a["user_id"] for a in alerts]
        count = len(user_ids)

        # Build one email body listing all high-risk users
        subject = f"[CDP] {count} high-risk users"
        lines = [f"- {uid}" for uid in user_ids] or ["(none)"]
        body = (
            "High-risk users in this run:\n"
            + "\n".join(lines)
            + f"\n\nCampaign: {args.campaign}\n— CDP Mailer\n"
        )

        # Send (unless dry-run)
        status = "skipped"
        error = None
        if not args.dry_run and count > 0:
            try:
                smtp = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10)
                if settings.smtp_user and settings.smtp_pass:
                    try:
                        smtp.starttls()
                    except Exception:
                        pass
                    smtp.login(settings.smtp_user, settings.smtp_pass)
                msg = EmailMessage()
                msg["From"] = settings.from_addr
                msg["To"] = args.recipient
                msg["Subject"] = subject
                msg.set_content(body)
                smtp.send_message(msg)
                smtp.quit()
                status = "sent"
            except Exception as e:
                status = "failed"
                error = str(e)

        # Mark all alerts as NOTIFIED and write notifications_log (one row per alert for audit)
        for a in alerts:
            q(conn, "UPDATE alerts SET status='NOTIFIED', campaign_id=%s, last_updated_at=now(), last_notified_at=now() WHERE alert_id=%s",
              (args.campaign, a["alert_id"]))
            q(conn, "INSERT INTO notifications_log(alert_id, user_id, campaign_id, status, error) VALUES (%s,%s,%s,%s,%s)",
              (a["alert_id"], a["user_id"], args.campaign, status, error))
        conn.commit()

    # JSON line log (single record for the run)
    log("email", "mailer",
        correlation_id=cid,
        campaign_id=args.campaign,
        aggregated=True,
        to_addr=args.recipient,
        count=count,
        status=status,
        error=error)
    
if __name__ == "__main__":
    main()
