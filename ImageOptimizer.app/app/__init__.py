from flask import Flask
from flask_cors import CORS
from .routes import main_bp
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for React frontend
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    app.register_blueprint(main_bp)

    return app
