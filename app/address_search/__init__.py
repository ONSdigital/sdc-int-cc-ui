from flask import Blueprint

address_search_bp = Blueprint('address_search', __name__)

from app.address_search import routes
