from flask import render_template
from flask import Blueprint
from user_auth import login_required

to_bp = Blueprint('to', __name__)


@to_bp.route('/to/')
@login_required
async def to_case_list():
    return render_template('to/list.html')
