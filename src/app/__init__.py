from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()


def create_app():
    app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    app = Flask(
        __name__,
        instance_path=os.path.join(app_root, "tmp"),
        instance_relative_config=True,
    )

    # Security configurations
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///roses.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Session security settings
    app.config["SESSION_COOKIE_SECURE"] = True  # Only send cookie over HTTPS
    app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent JavaScript access
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Prevent CSRF
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)  # Session timeout
    
    # CSRF protection settings
    app.config["WTF_CSRF_TIME_LIMIT"] = 3600  # CSRF token valid for 1 hour
    app.config["WTF_CSRF_SSL_STRICT"] = True  # Strict HTTPS checking
    
    # Content Security Policy headers
    @app.after_request
    def add_security_headers(response):
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Enable XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    from .models import User, Rose

    with app.app_context():
        db.create_all()

    from app.routes.auth import auth
    from app.routes.roses import roses

    app.register_blueprint(auth)
    app.register_blueprint(roses, url_prefix="/roses")

    return app
