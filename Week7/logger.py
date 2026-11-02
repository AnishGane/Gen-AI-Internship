"""Structured (JSON) logging + a tiny timer helper."""
import json, sys, time, logging
from contextlib import contextmanager

class JSONFormatter(logging.Formatter):
    def format(self, record):
        data = {"ts": self.formatTime(record), "level": record.levelname, "message": record.getMessage()}
        data.update(getattr(record, "extra_fields", {}))
        if record.exc_info:
            data["exc"] = self.formatException(record.exc_info)
        return json.dumps(data, default=str)

def get_logger(name: str = "rag") -> logging.Logger:
    log = logging.getLogger(name)
    if not log.handlers:
        h = logging.StreamHandler(sys.stderr)
        h.setFormatter(JSONFormatter())
        log.addHandler(h)
        log.setLevel(logging.INFO)
    return log

def log_event(log: logging.Logger, msg: str, **fields):
    log.info(msg, extra = {"extra_fields": fields})

@contextmanager
def timer(store: dict, key: str):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        store[key] = round((time.perf_counter() - t0) * 1000, 1) #ms