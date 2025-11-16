import logging, os, json, time
from .config import settings

class JsonLineFormatter(logging.Formatter):
    def format(self, record):
        base = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            base.update(record.extra)
        return json.dumps(base, separators=(",", ":"))

def get_logger(name="cdp"):
    os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(settings.log_file)
    fh.setFormatter(JsonLineFormatter())
    logger.addHandler(fh)
    return logger
