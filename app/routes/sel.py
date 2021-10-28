from flask import render_template, request, redirect, url_for, flash, current_app, get_flashed_messages, session
from app.utils import CCSvc, ProcessPostcode, Common
from app.routes.errors import InvalidDataError
from flask import Blueprint

sel_bp = Blueprint('sel', __name__)


@sel_bp.route('/sel/')
async def sel_home():
    return render_template('sel/home.html')


@sel_bp.route('/sel/input/', methods=['GET', 'POST'])
async def address_input():
    if request.method == 'POST':
        form_input = request.form['form_address_input']
        if form_input:
            return redirect(url_for('sel.addresses_by_input', input=request.form['form_address_input']))
        else:
            current_app.logger.info('Address input error: No value entered')
            flash('Enter an address value', 'error_input')
            return redirect(url_for('sel.address_input'))

    else:
        page_title = 'Enter an address'
        error_input = {}
        if get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            for message in get_flashed_messages():
                error_input = {'id': 'error_input', 'text': message}
        return render_template('sel/address-input.html',
                               page_title=page_title,
                               error_input=error_input)


@sel_bp.route('/sel/input/addresses/', methods=['GET', 'POST'])
async def addresses_by_input():
    if request.method == 'POST':
        if 'form-pick-address' in request.form:
            if request.form['form-pick-address'] == 'xxxx':
                return redirect(url_for('sel.address_not_found', address_input=request.args.get('input')))
            else:
                return redirect(url_for('sel.uprn_list', uprn=request.form['form-pick-address']))
        else:
            flash('Select an address', 'error_selection')
            return redirect(url_for('sel.addresses_by_input', input=request.args.get('input')))
    else:
        page_title = 'Select an address'
        error_selection = {}
        if get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            for message in get_flashed_messages():
                error_selection = {'id': 'error_selection', 'text': message}
        if request.args.get('input'):
            current_app.logger.info('Starting')
            cc_return = await CCSvc.get_addresses_by_input(request.args.get('input'))

            address_options = []

            cannot_find_text = "I cannot find the caller's address"

            for singleAddress in cc_return['addresses']:
                address_options.append({
                    'value': singleAddress['uprn'],
                    'label': {
                        'text': singleAddress['formattedAddress']
                    },
                    'id': singleAddress['uprn']
                })

            address_options.append({
                'value': 'xxxx',
                'label': {
                    'text': cannot_find_text
                },
                'id': 'xxxx'
            })

            address_content = {
                'addresses': address_options,
                'total_matches': cc_return['total']
            }

            return render_template('sel/address-results.html',
                                   page_title=page_title,
                                   results=address_content,
                                   error_selection=error_selection)
        else:
            return render_template('errors/500.html')


@sel_bp.route('/sel/postcode/', methods=['GET', 'POST'])
async def postcode_input():
    if request.method == 'POST':
        postcode_unvalidated = request.form['form_postcode_input']
        try:
            postcode = ProcessPostcode.validate_postcode(postcode_unvalidated)
            if 'values' in session:
                session.pop('values')
                session.modified = True
            return redirect(url_for('sel.addresses_by_postcode', postcode=postcode))
        except InvalidDataError as exc:
            current_app.logger.info(exc)
            flash(exc.message, 'error_postcode')
            session['values'] = {'postcode': postcode_unvalidated}
            session.modified = True
            return redirect(url_for('sel.postcode_input'))
    else:
        page_title = 'Enter a postcode'
        error_postcode = {}
        value_postcode = ''
        if get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            for message in get_flashed_messages():
                error_postcode = {'id': 'error_postcode', 'text': message}
                value_postcode = session['values']['postcode']
        return render_template('sel/postcode-input.html',
                               page_title=page_title,
                               error_postcode=error_postcode,
                               value_postcode=value_postcode)


@sel_bp.route('/sel/postcode/<postcode>', methods=['GET', 'POST'])
async def addresses_by_postcode(postcode):
    if request.method == 'POST':
        if 'form-pick-address' in request.form:
            if request.form['form-pick-address'] == 'xxxx':
                return redirect(url_for('sel.address_not_found', postcode=postcode))
            else:
                return redirect(url_for('sel.uprn_list', uprn=request.form['form-pick-address']))
        else:
            flash('Select an address', 'error_selection')
            return redirect(url_for('sel.addresses_by_postcode', postcode=postcode))
    else:
        page_title = 'Select an address'
        error_selection = {}
        if get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            for message in get_flashed_messages():
                error_selection = {'id': 'error_selection', 'text': message}
        if postcode:
            cc_return = await CCSvc.get_addresses_by_postcode(postcode)
            address_options = []
            cannot_find_text = "I cannot find the caller's address"
            for singleAddress in cc_return['addresses']:
                address_options.append({
                    'value': singleAddress['uprn'],
                    'label': {
                        'text': singleAddress['formattedAddress']
                    },
                    'id': singleAddress['uprn']
                })
            address_options.append({
                'value': 'xxxx',
                'label': {
                    'text': cannot_find_text
                },
                'id': 'xxxx'
            })
            address_content = {
                'postcode': postcode,
                'addresses': address_options,
                'total_matches': cc_return['total']
            }

            return render_template('sel/postcode-results.html',
                                   page_title=page_title,
                                   results=address_content,
                                   error_selection=error_selection)
        else:
            return render_template('errors/500.html')


@sel_bp.route('/sel/address-not-found', methods=['GET'])
async def address_not_found():
    page_title = 'Address not found'
    return render_template('sel/address-not-found.html',
                           page_title=page_title,
                           postcode=request.args.get('postcode'),
                           address_input=request.args.get('address_input'))


@sel_bp.route('/sel/uprn/<uprn>', methods=['GET'])
async def uprn_list(uprn):
    if uprn:
        cc_return = await CCSvc.get_case_by_uprn(uprn)
        case_list = []
        for single_case in cc_return:
            case_list.append({'text': 'Census 2021: Household',
                              'url': url_for('case.case', case_id=single_case['id'], org='sel')})

        address_output = ''
        addr_return = cc_return[0]['address']
        address_output = address_output + addr_return['addressLine1']
        if addr_return['addressLine2']:
            address_output = address_output + ', ' + addr_return['addressLine2']
        if addr_return['addressLine3']:
            address_output = address_output + ', ' + addr_return['addressLine3']
        if addr_return['townName']:
            address_output = address_output + ', ' + addr_return['townName']
        if addr_return['postcode']:
            address_output = address_output + ', ' + addr_return['postcode']

        return render_template('sel/uprn-list.html', uprn=uprn, address_output=address_output, case_list=case_list)
    else:
        return render_template('errors/500.html')
