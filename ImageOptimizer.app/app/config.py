import os
import secrets

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    # Add database configs, etc.
