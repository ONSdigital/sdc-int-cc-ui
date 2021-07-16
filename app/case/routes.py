from . import case_bp
from flask import render_template, request, redirect, url_for, flash, current_app
from app.utils import CCSvc, ProcessMobileNumber
from app.errors.handlers import InvalidDataError


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


@case_bp.route('/case/<case_id>/request-code-by-text/', methods=['GET', 'POST'])
async def case_request_code_by_text(case_id):
    if request.method == 'POST':
        if ('form-case-fulfilment' in request.form) and ('form-case-mobile-number' in request.form):

            try:
                mobile_number = \
                    ProcessMobileNumber.validate_uk_mobile_phone_number(request.form['form-case-mobile-number'])
                current_app.logger.info('valid mobile number')
                await CCSvc.post_sms_fulfilment(case_id, request.form['form-case-fulfilment'], mobile_number)
                return redirect(url_for('case.case_code_sent_by_text', case_id=case_id))
            except InvalidDataError as exc:
                current_app.logger.info(exc)
                flash(exc.message, 'error_mobile')
                error_mobile = exc.message
                return render_template('case/request-code-by-text.html', case_id=case_id, error_mobile=error_mobile)
        else:
            error_fulfilment = {}
            error_mobile = {}
            if not ('form-case-fulfilment' in request.form):
                flash('Select a fulfilment', 'error_fulfilment')
                error_fulfilment = {'id': 'error_fulfilment', 'text': 'Select a fulfilment'}
            if not ('form-case-mobile-number' in request.form):
                flash('Enter a mobile number', 'error_mobile')
                error_mobile = 'Enter a mobile number'
            return render_template('case/request-code-by-text.html',
                                   error_fulfilment=error_fulfilment,
                                   error_mobile=error_mobile)
    else:
        cc_return = await CCSvc.get_case_by_id(case_id)
        region = cc_return['region']
        current_app.logger.info('Region: ' + str(region))
        fulfilments = await CCSvc.get_fulfilments('UAC', 'SMS', region)

        if len(fulfilments) > 1:
            fulfilment_options = []
            for fulfilment in fulfilments:
                fulfilment_options.append({
                    'value': fulfilment['fulfilmentCode'],
                    'label': {
                        'text': fulfilment['description']
                    },
                    'id': fulfilment['fulfilmentCode']
                })
            return render_template('case/request-code-by-text.html', fulfilment_options=fulfilment_options)
        elif len(fulfilments) == 1:
            return render_template('case/request-code-by-text.html',
                                   fulfilment_code=fulfilments[0]['fulfilmentCode'])
        else:
            return render_template('errors/500.html')


@case_bp.route('/case/<case_id>/code-sent-by-text/', methods=['GET'])
async def case_code_sent_by_text(case_id):
    if case_id:
        return render_template('case/code-sent-by-text.html', case_id=case_id)
    else:
        return render_template('500.html')
