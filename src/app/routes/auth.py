from flask import Blueprint, request, jsonify, redirect, render_template, session
from markupsafe import escape

from app import db, bcrypt
from app.models import User

auth = Blueprint("auth", __name__)


@auth.route("/")
def index():
    return render_template("index.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        email = escape(data.get("email"))
        password = escape(data.get("password"))

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            return redirect("/roses"), 200
        else:
            return render_template("login.html", error="Invalid email or password"), 401
    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form

        email = escape(data.get("email"))
        password = escape(data.get("password"))

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 400

        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/")
