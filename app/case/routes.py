from . import case_bp
from flask import render_template, request, redirect, url_for, flash
from app.utils import CCSvc


@case_bp.route('/case/<case_id>', methods=['GET'])
async def case(case_id):
    if case_id:
        cc_return = await CCSvc.get_case_by_id(case_id)

        return render_template('case/case.html', case=cc_return, case_id=case_id)
    else:
        return render_template('500.html')


@case_bp.route('/case/<case_id>/request-refusal/', methods=['GET', 'POST'])
async def case_request_refusal(case_id):
    if request.method == 'POST':
        if 'form-case-request-refusal-reason' in request.form:
            reason = request.form['form-case-request-refusal-reason']
            if 'form-case-request-refusal-householder' in request.form:
                is_householder = True
            else:
                is_householder = False
            await CCSvc.post_case_refusal(case_id, reason, is_householder)
            return redirect(url_for('case.case_refused', case_id=case_id))
        else:
            flash('Select a reason', 'error_reason')
            return render_template('case/case-request-refusal.html', error_reason='Select an option')
    else:
        return render_template('case/case-request-refusal.html')


@case_bp.route('/case/<case_id>/refused/', methods=['GET'])
async def case_refused(case_id):
    if case_id:
        return render_template('case/case-refused.html', case_id=case_id)
    else:
        return render_template('500.html')
