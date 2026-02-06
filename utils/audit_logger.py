import json
import os
import datetime

AUDIT_FILE = "audit_log.json"

def _load_logs():
    if not os.path.exists(AUDIT_FILE):
        return []
    try:
        with open(AUDIT_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def _save_logs(logs):
    with open(AUDIT_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def log_event(username, action, details=None):
    """
    Logs an event to the audit trail.
    """
    logs = _load_logs()
    
    event = {
        "timestamp": str(datetime.datetime.now()),
        "user": username,
        "action": action,
        "details": details or {}
    }
    
    logs.append(event)
    _save_logs(logs)

def get_logs():
    """Returns all audit logs, newest first."""
    logs = _load_logs()
    return logs[::-1]
