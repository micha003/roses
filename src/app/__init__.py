from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import dotenv

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or os.urandom(24)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///roses.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    bcrypt.init_app(app)

    from .models import User

    with app.app_context():
        db.create_all()

    from app.routes.auth import auth
    from app.routes.roses import roses

    app.register_blueprint(auth)
    app.register_blueprint(roses, url_prefix="/roses")

    return app
