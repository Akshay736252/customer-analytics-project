"""
WSGI entry point for deployment
"""
from backend.main import app

# This is for gunicorn
application = app