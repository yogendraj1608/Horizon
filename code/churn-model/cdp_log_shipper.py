import os
import time
import json
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Elasticsearch Config
ES_HOST = "https://172.29.0.5:9200"
ES_USER = "elastic"
ES_PASS = "+P*67IIhXtQAfFz7_urk"
INDEX_NAME = "cdp_events"

# Resolve absolute log file path based on script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "cdp_events.log")

# Fields from all known log types
DEFAULT_FIELDS = {
    "@timestamp": None,
    "level": None,
    "message": None,
    "stage": None,
    "component": None,
    "correlation_id": None,
    "inserted": None,
    "users": None,
    "campaign_id": None,
    "aggregated": None,
    "to_addr": None,
    "count": None,
    "status": None,
    "error": None,
    "user_id": None,
    "intended_to": None,
    "segment": None
}

# Disable SSL warnings (for self-signed certs)
requests.packages.urllib3.disable_warnings()

def parse_log_line(line):
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        print(f"[INVALID JSON] {line}")
        return None

    if "ts" in data:
        data["@timestamp"] = data.pop("ts")

    return {**DEFAULT_FIELDS, **data}

def send_to_elasticsearch(doc):
    try:
        response = requests.post(
            f"{ES_HOST}/{INDEX_NAME}/_doc",
            auth=(ES_USER, ES_PASS),
            headers={"Content-Type": "application/json"},
            json=doc,
            verify=False
        )
        if response.status_code in [200, 201]:
            print(f"[OK] Sent log: {doc.get('message')} | {doc.get('correlation_id')}")
        else:
            print(f"[ERROR] {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[EXCEPTION] {e}")

def ingest_existing_logs():
    if not os.path.exists(LOG_FILE):
        print(f"[ERROR] Log file not found: {LOG_FILE}")
        return

    print("[INIT] Ingesting existing logs...")
    with open(LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            doc = parse_log_line(line)
            if doc:
                send_to_elasticsearch(doc)
    print("[DONE] Initial ingestion complete.")

class LogHandler(FileSystemEventHandler):
    def __init__(self, filepath):
        self.filepath = filepath
        self.position = os.path.getsize(filepath)

    def on_modified(self, event):
        if event.src_path != self.filepath:
            return
        with open(self.filepath, "r") as f:
            f.seek(self.position)
            new_lines = f.readlines()
            self.position = f.tell()
        for line in new_lines:
            line = line.strip()
            if not line:
                continue
            doc = parse_log_line(line)
            if doc:
                send_to_elasticsearch(doc)

def monitor_log_file():
    print("[WATCH] Starting live monitoring...")

    if not os.path.exists(LOG_FILE):
        print(f"[ERROR] Log file does not exist: {LOG_FILE}")
        return

    event_handler = LogHandler(LOG_FILE)
    observer = Observer()
    observer.schedule(event_handler, path=BASE_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[EXIT] Stopping monitor...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    ingest_existing_logs()
    monitor_log_file()
