import flask

from . import case_bp
from flask import render_template, request, redirect, url_for, flash, current_app, session
from app.utils import CCSvc, ProcessMobileNumber, ProcessContactNumber, ProcessJsonForOptions, Common
from app.errors.handlers import InvalidDataError


@case_bp.route('/case/<case_id>/', methods=['GET'])
async def case(case_id):
    if case_id:
        page_title = 'Case ' + case_id
        cc_return = await CCSvc.get_case_by_id(case_id)

        return render_template('case/case.html', case=cc_return, case_id=case_id, page_title=page_title)
    else:
        return render_template('errors/500.html')


@case_bp.route('/case/<case_id>/add-case-note/', methods=['GET', 'POST'])
async def add_case_note(case_id):
    if request.method == 'POST':
        if 'form-case-add-note' in request.form:
            # TODO  add case note endpoint call
            return redirect(url_for('case.case_note_added', case_id=case_id))
        else:
            flash('Add a note', 'error_note')
            return redirect(url_for('case.add_case_note', case_id=case_id))
    else:
        page_title = 'Add case note'
        error_note = {}
        if flask.get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            error_note = {'id': 'error_reason', 'text': 'Add note'}
        return render_template('case/add-note.html', case_id=case_id, page_title=page_title, error_note=error_note)


@case_bp.route('/case/<case_id>/case-note-added/', methods=['GET'])
async def case_note_added(case_id):
    if case_id:
        return render_template('case/case-note-added.html', case_id=case_id)
    else:
        return render_template('errors/500.html')


@case_bp.route('/case/<case_id>/request-refusal/', methods=['GET', 'POST'])
async def request_refusal(case_id):
    if request.method == 'POST':
        if 'form-case-request-refusal-reason' in request.form:
            reason = request.form['form-case-request-refusal-reason']
            if 'form-case-request-refusal-householder' in request.form:
                is_householder = True
            else:
                is_householder = False
            await CCSvc.post_case_refusal(case_id, reason, is_householder)
            return redirect(url_for('case.refused', case_id=case_id))
        else:
            flash('Select a reason', 'error_reason')
            return redirect(url_for('case.request_refusal', case_id=case_id))
    else:
        page_title = 'Request refusal'
        error_reason = {}
        if flask.get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            error_reason = {'id': 'error_reason', 'text': 'Select an option'}

        return render_template('case/request-refusal.html',
                               case_id=case_id,
                               page_title=page_title,
                               error_reason=error_reason)


@case_bp.route('/case/<case_id>/refused/', methods=['GET'])
async def refused(case_id):
    if case_id:
        return render_template('case/refused.html', case_id=case_id)
    else:
        return render_template('errors/500.html')


@case_bp.route('/case/<case_id>/request-code-by-text/', methods=['GET', 'POST'])
async def request_code_by_text(case_id):
    if request.method == 'POST':
        session['values'] = {}
        valid_fulfilment = True
        valid_mobile_number = True
        mobile_number = ''
        if 'form-case-fulfilment' in request.form:
            session['values']['fulfilment'] = request.form['form-case-fulfilment']
            session.modified = True
        else:
            flash(Common.message_select_fulfilment, 'error_fulfilment')
            valid_fulfilment = False

        if 'form-case-mobile-number' in request.form:
            try:
                mobile_number = \
                    ProcessMobileNumber.validate_uk_mobile_phone_number(request.form['form-case-mobile-number'])
                current_app.logger.info('valid mobile number')
            except InvalidDataError as exc:
                current_app.logger.info(exc)
                flash(exc.message, 'error_mobile')
                session['values']['mobile'] = request.form['form-case-mobile-number']
                session.modified = True
                valid_mobile_number = False
        else:
            flash(Common.message_enter_mobile, 'error_mobile')
            valid_mobile_number = False

        if valid_fulfilment and valid_mobile_number:
            await CCSvc.post_sms_fulfilment(case_id, request.form['form-case-fulfilment'], mobile_number)
            if 'values' in session:
                session.pop('values')
                session.modified = True
            return redirect(url_for('case.code_sent_by_text', case_id=case_id))
        else:
            return redirect(url_for('case.request_code_by_text', case_id=case_id))

    else:
        page_title = 'Request code by text'

        error_fulfilment = {}
        error_mobile = {}
        value_fulfilment = ''
        value_mobile = ''
        if flask.get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            if 'values' in session:
                value_fulfilment = session['values'].get('fulfilment')
                value_mobile = session['values'].get('mobile')
            if flask.get_flashed_messages(category_filter=['error_fulfilment']):
                for message in flask.get_flashed_messages():
                    error_fulfilment = {'id': 'error_fulfilment', 'text': message}
            if flask.get_flashed_messages(category_filter=['error_mobile']):
                for message in flask.get_flashed_messages():
                    error_mobile = {'id': 'error_mobile', 'text': message}

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
            return render_template('case/request-code-by-text.html',
                                   fulfilment_options=fulfilment_options,
                                   page_title=page_title,
                                   case_id=case_id,
                                   error_fulfilment=error_fulfilment,
                                   error_mobile=error_mobile,
                                   value_fulfilment=value_fulfilment,
                                   value_mobile=value_mobile)
        elif len(fulfilments) == 1:
            return render_template('case/request-code-by-text.html',
                                   fulfilment_code=fulfilments[0]['fulfilmentCode'],
                                   page_title=page_title,
                                   case_id=case_id,
                                   error_mobile=error_mobile,
                                   value_mobile=value_mobile)
        else:
            return render_template('errors/500.html')


@case_bp.route('/case/<case_id>/code-sent-by-text/', methods=['GET'])
async def code_sent_by_text(case_id):
    if case_id:
        return render_template('case/code-sent-by-text.html', case_id=case_id)
    else:
        return render_template('errors/500.html')


@case_bp.route('/case/<case_id>/request-code-by-post/', methods=['GET', 'POST'])
async def request_code_by_post(case_id):
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

            await CCSvc.post_postal_fulfilment(case_id,
                                               fulfilment_code,
                                               request.form['form-case-first-name'],
                                               request.form['form-case-last-name'])
            if 'values' in session:
                session.pop('values')
                session.modified = True
            return redirect(url_for('case.code_sent_by_post', case_id=case_id))

        else:
            session['values'] = {}
            if not ('form-case-first-name' in request.form) or request.form['form-case-first-name'] == '':
                flash('Enter a first name', 'error_first_name')
            else:
                if not len(request.form['form-case-first-name']) <= 35:
                    flash('You have entered too many characters. Enter up to 35 characters', 'error_first_name')
                session['values']['first_name'] = request.form['form-case-first-name']

            if not ('form-case-last-name' in request.form) or request.form['form-case-last-name'] == '':
                flash('Enter a last name', 'error_last_name')
            else:
                if not len(request.form['form-case-last-name']) <= 35:
                    flash('You have entered too many characters. Enter up to 35 characters', 'error_last_name')
                session['values']['last_name'] = request.form['form-case-last-name']

            session.modified = True
            return redirect(url_for('case.request_code_by_post', case_id=case_id))
    else:
        page_title = 'Request code by post'

        error_first_name = {}
        error_last_name = {}
        value_first_name = ''
        value_last_name = ''
        if flask.get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            if 'values' in session:
                value_first_name = session['values'].get('first_name')
                value_last_name = session['values'].get('last_name')
            if flask.get_flashed_messages(category_filter=['error_first_name']):
                for message in flask.get_flashed_messages():
                    error_first_name = {'id': 'error_first_name', 'text': message}
            if flask.get_flashed_messages(category_filter=['error_last_name']):
                for message in flask.get_flashed_messages():
                    error_last_name = {'id': 'error_last_name', 'text': message}

        cc_return = await CCSvc.get_case_by_id(case_id)
        region = cc_return['region']
        fulfilments = await CCSvc.get_fulfilments('UAC', 'POST', region)
        if len(fulfilments) == 1:
            return render_template('case/request-code-by-post.html',
                                   page_title=page_title,
                                   case_id=case_id,
                                   fulfilment_code=fulfilments[0]['fulfilmentCode'],
                                   error_first_name=error_first_name,
                                   error_last_name=error_last_name,
                                   value_first_name=value_first_name,
                                   value_last_name=value_last_name)
        else:
            return render_template('errors/500.html')


@case_bp.route('/case/<case_id>/code-sent-by-post/', methods=['GET'])
async def code_sent_by_post(case_id):
    if case_id:
        return render_template('case/code-sent-by-post.html', case_id=case_id)
    else:
        return render_template('errors/500.html')


@case_bp.route('/case/<case_id>/update-contact-number/', methods=['GET', 'POST'])
async def update_contact_number(case_id):
    if request.method == 'POST':
        if 'form-case-contact-number' in request.form:
            try:
                contact_number = \
                    ProcessContactNumber.validate_uk_phone_number(request.form['form-case-contact-number'])
                current_app.logger.info('valid contact number')
                # TODO  add update contact number endpoint call
                if 'values' in session:
                    session.pop('values')
                    session.modified = True
                return redirect(url_for('case.contact_number_updated', case_id=case_id))
            except InvalidDataError as exc:
                current_app.logger.info(exc)
                flash(exc.message, 'error_contact_number')
                session['values'] = {'contact_number': request.form['form-case-contact-number']}
                session.modified = True
                return redirect(url_for('case.update_contact_number', case_id=case_id))
        else:
            flash(Common.message_contact_number, 'error_contact_number')
            return redirect(url_for('case.update_contact_number', case_id=case_id))

    else:
        page_title = 'Update contact number'
        error_contact_number = {}
        value_contact_number = ''
        if flask.get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            for message in flask.get_flashed_messages():
                if message == Common.message_contact_number:
                    error_contact_number = {'id': 'error_contact_number', 'text': Common.message_contact_number}
                else:
                    error_contact_number = {'id': 'error_contact_number', 'text': message}
            if 'values' in session:
                value_contact_number = session['values'].get('contact_number')
        return render_template('case/update-contact-number.html',
                               case_id=case_id,
                               page_title=page_title,
                               error_contact_number=error_contact_number,
                               value_contact_number=value_contact_number)


@case_bp.route('/case/<case_id>/contact-number-updated/', methods=['GET'])
async def contact_number_updated(case_id):
    if case_id:
        return render_template('case/contact-number-updated.html', case_id=case_id)
    else:
        return render_template('errors/500.html')


@case_bp.route('/case/<case_id>/call-outcome/', methods=['GET', 'POST'])
async def call_outcome(case_id):
    if request.method == 'POST':
        if 'form-case-call-type' in request.form and 'form-case-call-outcome' in request.form:
            # TODO  add call outcome endpoint call
            if 'values' in session:
                session.pop('values')
                session.modified = True
            return redirect(url_for('case.call_outcome_recorded', case_id=case_id))
        else:
            if not ('form-case-call-type' in request.form):
                flash(Common.message_select_call_type, 'error_call_type')
            else:
                session['values'] = {'call_type': request.form['form-case-call-type']}
                session.modified = True
            if not ('form-case-call-outcome' in request.form):
                flash(Common.message_select_call_outcome, 'error_call_outcome')
            else:
                session['values'] = {'call_outcome': request.form['form-case-call-outcome']}
                session.modified = True
            return redirect(url_for('case.call_outcome', case_id=case_id))

    else:
        page_title = 'Record call outcome'
        error_call_type = {}
        error_call_outcome = {}
        value_call_type = ''
        value_call_outcome = ''
        if flask.get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            for message in flask.get_flashed_messages():
                if message == Common.message_select_call_type:
                    error_call_type = {'id': 'error_call_type', 'text': Common.message_select_option}
                if message == Common.message_select_call_outcome:
                    error_call_outcome = {'id': 'error_call_outcome', 'text': Common.message_select_option}
            if 'values' in session:
                value_call_type = session['values'].get('call_type')
                value_call_outcome = session['values'].get('call_outcome')

        call_type_options = ProcessJsonForOptions.options_from_json('call-type.json')
        call_outcome_options = ProcessJsonForOptions.options_from_json('outcome-codes.json')

        return render_template('case/call-outcome.html',
                               page_title=page_title,
                               case_id=case_id,
                               call_type_options=call_type_options,
                               call_outcome_options=call_outcome_options,
                               error_call_type=error_call_type,
                               error_call_outcome=error_call_outcome,
                               value_call_type=value_call_type,
                               value_call_outcome=value_call_outcome)


@case_bp.route('/case/<case_id>/call-outcome-recorded/', methods=['GET'])
async def call_outcome_recorded(case_id):
    if case_id:
        return render_template('case/call-outcome-recorded.html', case_id=case_id)
    else:
        return render_template('errors/500.html')


@case_bp.route('/case/<case_id>/data-removal-request/', methods=['GET', 'POST'])
async def data_removal_request(case_id):
    if request.method == 'POST':
        if 'form-case-data-removal-request' in request.form:
            if request.form['form-case-data-removal-request'] == 'yes':
                # TODO  add call outcome endpoint call
                return redirect(url_for('case.data_removed', case_id=case_id))
            else:
                return redirect(url_for('case.case', case_id=case_id))
        else:
            flash('Confirm data removal request', 'error_confirmation')
            return redirect(url_for('case.data_removal_request', case_id=case_id))
    else:
        page_title = 'Data removal request'
        error_confirmation = {}
        if flask.get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            error_confirmation = {'id': 'error_confirmation', 'text': 'Select an option'}

        return render_template('case/data-removal-request.html',
                               case_id=case_id,
                               page_title=page_title,
                               error_confirmation=error_confirmation)


@case_bp.route('/case/<case_id>/data-removed/', methods=['GET'])
async def data_removed(case_id):
    if case_id:
        return render_template('case/data-removed.html', case_id=case_id)
    else:
        return render_template('errors/500.html')
