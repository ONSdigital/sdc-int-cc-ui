from . import case_bp
from flask import render_template, request, redirect, url_for, flash, current_app
from app.utils import CCSvc, ProcessMobileNumber, ProcessContactNumber
from app.errors.handlers import InvalidDataError


@case_bp.route('/case/<case_id>/', methods=['GET'])
async def case(case_id):
    if case_id:
        cc_return = await CCSvc.get_case_by_id(case_id)

        return render_template('case/case.html', case=cc_return, case_id=case_id)
    else:
        return render_template('500.html')


@case_bp.route('/case/<case_id>/add-case-note/', methods=['GET', 'POST'])
async def case_add_case_note(case_id):
    if request.method == 'POST':
        if 'form-case-add-note' in request.form:
            # TODO  add case note endpoint call
            return redirect(url_for('case.case_note_added', case_id=case_id))
        else:
            flash('Add a note', 'error_note')
            return render_template('case/case-add-note.html', error_note='Add note')
    else:
        return render_template('case/case-add-note.html', case_id=case_id)


@case_bp.route('/case/<case_id>/case-note-added/', methods=['GET'])
async def case_note_added(case_id):
    if case_id:
        return render_template('case/case-note-added.html', case_id=case_id)
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
        return render_template('case/case-request-refusal.html', case_id=case_id)


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
                                   fulfilment_code=fulfilments[0]['fulfilmentCode'], case_id=case_id)
        else:
            return render_template('errors/500.html')


@case_bp.route('/case/<case_id>/code-sent-by-text/', methods=['GET'])
async def case_code_sent_by_text(case_id):
    if case_id:
        return render_template('case/code-sent-by-text.html', case_id=case_id)
    else:
        return render_template('500.html')


@case_bp.route('/case/<case_id>/request-code-by-post/', methods=['GET', 'POST'])
async def case_request_code_by_post(case_id):
    if request.method == 'POST':
        if 'form-case-fulfilment' in request.form:
            fulfilment_code = request.form['form-case-fulfilment']
        else:
            cc_return = await CCSvc.get_case_by_id(case_id)
            region = cc_return['region']
            fulfilments = await CCSvc.get_fulfilments('UAC', 'POST', region)
            fulfilment_code = fulfilments[0]['fulfilmentCode']

        if ('form-case-first-name' in request.form) and request.form['form-case-first-name'] != '' \
                and len(request.form['form-case-first-name']) <= 35 \
                and ('form-case-last-name' in request.form) and request.form['form-case-last-name'] != '' \
                and len(request.form['form-case-last-name']) <= 35:
            try:
                await CCSvc.post_postal_fulfilment(case_id,
                                                   fulfilment_code,
                                                   request.form['form-case-first-name'],
                                                   request.form['form-case-last-name'])
                return redirect(url_for('case.case_code_sent_by_post', case_id=case_id))
            except InvalidDataError as exc:
                current_app.logger.info(exc)
                flash(exc.message, 'error_mobile')
                error_mobile = exc.message
                return render_template('case/request-code-by-post.html', case_id=case_id, error_mobile=error_mobile)
        else:
            if not ('form-case-first-name' in request.form) or request.form['form-case-first-name'] == '':
                flash('Enter a first name', 'error_first_name')
                error_first_name = {'id': 'error_first_name', 'text': 'Enter a first name'}
                first_name_value = ''
            elif not len(request.form['form-case-first-name']) <= 35:
                flash('You have entered too many characters. Enter up to 35 characters', 'error_first_name')
                error_first_name = {'id': 'error_first_name',
                                    'text': 'You have entered too many characters. Enter up to 35 characters'}
                first_name_value = request.form['form-case-first-name']
            else:
                error_first_name = {}
                first_name_value = request.form['form-case-first-name']

            if not ('form-case-last-name' in request.form) or request.form['form-case-last-name'] == '':
                flash('Enter a last name', 'error_last_name')
                error_last_name = {'id': 'error_last_name', 'text': 'Enter a last name'}
                last_name_value = ''
            elif not len(request.form['form-case-last-name']) <= 35:
                flash('You have entered too many characters. Enter up to 35 characters', 'error_last_name')
                error_last_name = \
                    {'id': 'error_last_name', 'text': 'You have entered too many characters. Enter up to 35 characters'}
                last_name_value = request.form['form-case-last-name']
            else:
                error_last_name = {}
                last_name_value = request.form['form-case-last-name']

            return render_template('case/request-code-by-post.html',
                                   error_first_name=error_first_name,
                                   error_last_name=error_last_name,
                                   first_name=first_name_value,
                                   last_name=last_name_value,
                                   fulfilment_code=fulfilment_code)
    else:
        cc_return = await CCSvc.get_case_by_id(case_id)
        region = cc_return['region']
        fulfilments = await CCSvc.get_fulfilments('UAC', 'POST', region)
        if len(fulfilments) == 1:
            return render_template('case/request-code-by-post.html',
                                   fulfilment_code=fulfilments[0]['fulfilmentCode'], case_id=case_id)
        else:
            return render_template('errors/500.html')


@case_bp.route('/case/<case_id>/code-sent-by-post/', methods=['GET'])
async def case_code_sent_by_post(case_id):
    if case_id:
        return render_template('case/code-sent-by-post.html', case_id=case_id)
    else:
        return render_template('500.html')


@case_bp.route('/case/<case_id>/update-contact-number/', methods=['GET', 'POST'])
async def case_update_contact_number(case_id):
    if request.method == 'POST':
        if 'form-case-contact-number' in request.form:
            try:
                contact_number = \
                    ProcessContactNumber.validate_uk_phone_number(request.form['form-case-contact-number'])
                current_app.logger.info('valid contact number')
                # TODO  add update contact number endpoint call
                return redirect(url_for('case.case_contact_number_updated', case_id=case_id))
            except InvalidDataError as exc:
                current_app.logger.info(exc)
                flash(exc.message, 'error_contact_number')
                error_contact_number = {'id': 'error_contact_number', 'text': exc.message}
                return render_template('case/case-update-contact-number.html',
                                       case_id=case_id,
                                       error_contact_number=error_contact_number)
        else:
            if not ('form-case-contact-number' in request.form):
                flash('Enter a contact number', 'error_contact_number')
                error_contact_number = {'id': 'error_contact_number', 'text': 'Enter a contact number'}
            else:
                error_contact_number = {}
            return render_template('case/request-code-by-text.html', error_contact_number=error_contact_number)

    else:
        return render_template('case/case-update-contact-number.html', case_id=case_id)


@case_bp.route('/case/<case_id>/contact-number-updated/', methods=['GET'])
async def case_contact_number_updated(case_id):
    if case_id:
        return render_template('case/case-contact-number-updated.html', case_id=case_id)
    else:
        return render_template('500.html')
