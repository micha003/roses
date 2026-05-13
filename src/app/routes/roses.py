from flask import Blueprint, request, jsonify, render_template, redirect
from markupsafe import escape

from app import db
from app.models import Rose

# from app.models import Rose

roses = Blueprint("roses", __name__)

# Wrapper

from functools import wraps
from flask import session


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return fn(*args, **kwargs)

    return wrapper


@login_required
@roses.route("/")
def dashboard():
    return render_template("roses_dashboard.html")


@login_required
@roses.route("/send_rose", methods=["GET", "POST"])
def send_rose():
    if request.method == "POST":
        data = request.form

        # Collection of Data for Rose Sending
        sender_email = db.Query.text(
            f"SELECT email FROM user WHERE id=:{session['user_id']}"
        ).first()[0]
        sender_name = db.Query.text(
            f"SELECT name FROM user WHERE id=:{session['user_id']}"
        ).first()[0]
        recipient_email = escape(data.get("recipient_email"))
        recipient_name = escape(data.get("recipient_name"))
        message = escape(data.get("message"))

        new_rose = Rose(
            sender_email=sender_email,
            sender_name=sender_name,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            message=message,
        )

        db.session.add(new_rose)
        db.session.commit()

    return render_template("send_rose.html")
