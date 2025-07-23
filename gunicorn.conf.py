# Gunicorn Configuration for SLHS Wrestling
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server socket
bind = f"{os.getenv('FLASK_HOST', '0.0.0.0')}:{os.getenv('FLASK_PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', '2'))
worker_class = 'sync'
worker_connections = 1000
timeout = int(os.getenv('TIMEOUT', '120'))
keepalive = 2
max_requests = 1000
max_requests_jitter = 50

# Restart workers to prevent memory leaks
preload_app = True

# Logging
accesslog = '/var/log/slhs-wrestling/access.log'
errorlog = '/var/log/slhs-wrestling/error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'slhs-wrestling'

# Server mechanics
daemon = False
pidfile = '/var/run/slhs-wrestling.pid'
tmp_upload_dir = None

# SSL (for future HTTPS setup)
# keyfile = None
# certfile = None 