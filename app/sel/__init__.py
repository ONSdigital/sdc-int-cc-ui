from flask import Blueprint

sel_bp = Blueprint('sel', __name__)

from app.sel import routes
