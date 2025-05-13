import os
import multiprocessing

# Gunicorn configuration file
# This ensures proper application context handling

# Bind to the port provided by Render
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker configuration
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
threads = 2
timeout = 120

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Set environment variable to indicate we're running on Render
raw_env = ["RENDER=true"]

# Preload the application to ensure application context is set up properly
preload_app = True

# This function is called when worker processes are forked
def post_fork(server, worker):
    server.log.info("Worker spawned")

# This function is called when the master process is initialized
def on_starting(server):
    server.log.info("Starting Gunicorn server with application context")
