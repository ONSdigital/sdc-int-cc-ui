from . import to_bp
from flask import render_template


@to_bp.route('/to/')
async def to_case_list():
    return render_template('to/list.html')
