from . import case_bp
from flask import render_template
from app.utils import CCSvc


@case_bp.route('/case/<case_id>', methods=['GET'])
async def case(case_id):
    if case_id:
        cc_return = await CCSvc.get_case_by_id(case_id)

        return render_template('case/case.html', case=cc_return)
    else:
        return render_template('500.html')