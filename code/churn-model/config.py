import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    pg_dsn: str = os.getenv("PG_DSN", "postgresql://cdpuser:cdppass@localhost:5432/cdp")
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.mailgun.org")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "user@sandbox52f41531319c478fba1d29b17a6a36d1.mailgun.org")
    smtp_pass: str = os.getenv("SMTP_PASS", "Jain@1209aqzr")
    from_addr: str = os.getenv("FROM_ADDR", "jainyogendra1685@gmail.com")
    log_file: str = os.getenv("LOG_FILE", "logs/cdp_events.log")
    window_days: int = int(os.getenv("WINDOW_DAYS", "14"))
    score_threshold_high: float = float(os.getenv("SCORE_THRESHOLD_HIGH", "0.70"))
    score_threshold_med: float = float(os.getenv("SCORE_THRESHOLD_MED", "0.50"))
    cooldown_days: int = int(os.getenv("COOLDOWN_DAYS", "7"))

settings = Settings()
