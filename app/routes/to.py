from flask import render_template, session, url_for
from flask import Blueprint
from app.user_auth import login_required

to_bp = Blueprint('to', __name__)


@to_bp.route('/to/')
@login_required
async def to_case_list():
    session['back_url'] = url_for('to.to_case_list')
    return render_template('to/list.html')
