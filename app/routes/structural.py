from flask import Blueprint
from flask import render_template

structural_bp = Blueprint("structural", __name__)


@structural_bp.route('/')
async def home():
    return render_template('home.html')
