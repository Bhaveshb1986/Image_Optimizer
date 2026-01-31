import os
import secrets

# Project root: directory containing the "app" package (parent of this file's dir)
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    # Absolute path so uploads are always in project root /uploads (e.g. ImageOptimizer.app/uploads)
    UPLOAD_FOLDER = os.path.join(_ROOT, 'uploads')
    # Add database configs, etc.
