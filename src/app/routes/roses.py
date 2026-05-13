from flask import Blueprint, request, jsonify, render_template, redirect
from markupsafe import escape

from app import db

# from app.models import Rose

roses = Blueprint("roses", __name__)


@roses.route("/")
def rose():
    return render_template("roses.html")
