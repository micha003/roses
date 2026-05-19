from flask import Blueprint, request, render_template, redirect, session, flash
from markupsafe import escape

from app import db
from app.models import Rose, User
from app.utils.validators import (
    is_valid_email,
    is_valid_name,
    is_valid_message,
    sanitize_string,
    rate_limit
)

from functools import wraps

roses = Blueprint("roses", __name__)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return fn(*args, **kwargs)
    return wrapper


@roses.route("/")
@login_required
def dashboard():
    return render_template("roses_dashboard.html")


@roses.route("/send_rose", methods=["GET", "POST"])
@login_required
@rate_limit(max_requests=10, window_seconds=60)  # Max 10 roses per minute
def send_rose():
    if request.method == "POST":
        data = request.form

        # Get current user safely using ORM (no raw SQL)
        user_id = session.get('user_id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            flash("Session expired. Please log in again.", "error")
            return redirect("/login")

        # Sanitize and validate recipient email
        recipient_email = sanitize_string(data.get("recipient_email", ""), max_length=254)
        is_valid, error_msg = is_valid_email(recipient_email)
        if not is_valid:
            flash(f"Invalid recipient email: {error_msg}", "error")
            return render_template("send_rose.html")

        # Sanitize and validate recipient name
        recipient_name = sanitize_string(data.get("recipient_name", ""), max_length=100)
        is_valid, error_msg = is_valid_name(recipient_name)
        if not is_valid:
            flash(f"Invalid recipient name: {error_msg}", "error")
            return render_template("send_rose.html")

        # Sanitize and validate message
        message = sanitize_string(data.get("message", ""), max_length=500)
        is_valid, error_msg = is_valid_message(message)
        if not is_valid:
            flash(f"Invalid message: {error_msg}", "error")
            return render_template("send_rose.html")

        # Escape all user inputs for XSS protection before storing
        recipient_email = escape(recipient_email)
        recipient_name = escape(recipient_name)
        message = escape(message)

        # Create rose using ORM (parameterized, safe from SQL injection)
        new_rose = Rose(
            sender_id=current_user.id,
            sender_name=escape(current_user.name or "Anonymous"),
            recipient_email=recipient_email,
            message=message,
        )

        db.session.add(new_rose)
        db.session.commit()

        # Send the email
        try:
            from app.Scripts.send_rose import send_email
            sender_display_name = current_user.name or "Someone special"
            send_email(sender_display_name, str(recipient_email), str(message))
            flash("Your rose has been sent!", "success")
        except Exception as e:
            # Log the error but don't expose details to user
            print(f"[v0] Email sending failed: {e}")
            flash("Rose saved but email delivery may be delayed.", "warning")

        return redirect("/roses")

    return render_template("send_rose.html")
