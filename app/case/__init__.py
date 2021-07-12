from flask import Blueprint

case_bp = Blueprint('case', __name__)

from app.case import routes
