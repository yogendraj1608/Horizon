import os, json, uuid, time, math, statistics
from datetime import datetime, timedelta, timezone
from .logger import get_logger

logger = get_logger()

def now_utc():
    return datetime.now(timezone.utc)

def iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def corr_id():
    return str(uuid.uuid4())

def log(stage, component, **fields):
    logger.info(stage, extra={"extra": {"stage": stage, "component": component, **fields}})

def days_between(ts1, ts2):
    return abs((ts2 - ts1).total_seconds())/86400.0

def moving_avg_days(timestamps):
    if len(timestamps) < 2:
        return None
    days = [days_between(timestamps[i-1], timestamps[i]) for i in range(1, len(timestamps))]
    return sum(days)/len(days)
