from flask import Blueprint
from flask import render_template
from structlog import get_logger
from app.access import load_permissions

structural_bp = Blueprint("structural", __name__)

logger = get_logger()


@structural_bp.route('/')
@load_permissions
async def home():
    logger.debug('Home')
    return render_template('home.html')
