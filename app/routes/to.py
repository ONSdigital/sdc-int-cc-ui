from flask import render_template
from flask import Blueprint

to_bp = Blueprint('to', __name__)


@to_bp.route('/to/')
async def to_case_list():
    return render_template('to/list.html')
