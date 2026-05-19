from flask import Blueprint, request, redirect, render_template, session, flash
from markupsafe import escape

from app import db, bcrypt
from app.models import User
from app.utils.validators import (
    is_valid_email,
    is_valid_password,
    sanitize_string,
    rate_limit
)

auth = Blueprint("auth", __name__)


@auth.route("/")
def index():
    return render_template("index.html")


@auth.route("/login", methods=["GET", "POST"])
@rate_limit(max_requests=5, window_seconds=60)  # Max 5 login attempts per minute
def login():
    if request.method == "POST":
        data = request.form
        
        # Sanitize inputs
        email = sanitize_string(data.get("email", ""), max_length=254).lower()
        password = data.get("password", "")  # Don't sanitize password as it may contain special chars

        # Validate email format
        is_valid, error_msg = is_valid_email(email)
        if not is_valid:
            return render_template("login.html", error="Invalid email or password"), 401

        # Use ORM for safe parameterized query (no SQL injection possible)
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Regenerate session to prevent session fixation
            session.clear()
            session["user_id"] = user.id
            session.permanent = True  # Use permanent session with timeout
            return redirect("/roses")
        else:
            # Use generic error message to prevent user enumeration
            return render_template("login.html", error="Invalid email or password"), 401
    
    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
@rate_limit(max_requests=3, window_seconds=60)  # Max 3 registrations per minute
def register():
    if request.method == "POST":
        data = request.form

        # Sanitize and validate email
        email = sanitize_string(data.get("email", ""), max_length=254).lower()
        is_valid, error_msg = is_valid_email(email)
        if not is_valid:
            flash(error_msg, "error")
            return render_template("register.html")

        # Validate password
        password = data.get("password", "")
        is_valid, error_msg = is_valid_password(password)
        if not is_valid:
            flash(error_msg, "error")
            return render_template("register.html")

        # Check if email already exists using ORM (safe from SQL injection)
        if User.query.filter_by(email=email).first():
            # Use generic message to prevent user enumeration
            flash("Unable to create account. Please try a different email.", "error")
            return render_template("register.html")

        # Create new user with escaped email
        new_user = User(email=escape(email))
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect("/login")

    return render_template("register.html")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/")
