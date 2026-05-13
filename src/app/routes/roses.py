from flask import Blueprint, request, jsonify, render_template, redirect
from markupsafe import escape

from app import db

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

    return render_template("send_rose.html")
