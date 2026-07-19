"""Gunicorn configuration for StadiumIQ with Socket.IO support."""
import os

bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = int(os.getenv("GUNICORN_WORKERS", "1"))
worker_class = "gthread"
threads = int(os.getenv("GUNICORN_THREADS", "4"))
timeout = 60
keepalive = 5
max_requests = 200
max_requests_jitter = 25
limit_request_line = 8190
limit_request_field_size = 8190
accesslog = "-"
errorlog = "-"
loglevel = "info"
