from flask import Blueprint

to_bp = Blueprint('to', __name__)

from app.to import routes
