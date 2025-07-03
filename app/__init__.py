from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables from .env
    load_dotenv()

    app = Flask(__name__)

    # Register routes from routes.py
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
