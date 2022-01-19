from flask import Blueprint, current_app
from flask import render_template
from user_auth import login_required

structural_bp = Blueprint("structural", __name__)


@structural_bp.route('/')
async def home():
    current_app.logger.info('Home')
    return render_template('home.html')
