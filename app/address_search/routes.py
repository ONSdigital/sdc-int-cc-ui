from . import address_search_bp
from flask import render_template, request, redirect, url_for, flash, current_app, get_flashed_messages
from app.utils import CCSvc, ProcessPostcode, Common
from app.errors.handlers import InvalidDataError


@address_search_bp.route('/addresses/', methods=['GET', 'POST'])
async def address_input():
    if request.method == 'POST':
        form_input = request.form['form_address_input']
        if form_input:
            return redirect(url_for('address_search.addresses_by_input', input=request.form['form_address_input']))
        else:
            current_app.logger.info('Address input error: No value entered')
            flash('Enter an address value', 'error_input')
            return redirect(url_for('address_search.address_input'))

    else:
        page_title = 'Enter an address'
        error_input = {}
        if get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            for message in get_flashed_messages():
                error_input = {'id': 'error_input', 'text': message}
        return render_template('address-search/address-input.html',
                               page_title=page_title,
                               error_input=error_input)


@address_search_bp.route('/addresses/input/', methods=['GET', 'POST'])
async def addresses_by_input():
    if request.method == 'POST':
        if 'form-pick-address' in request.form:
            if request.form['form-pick-address'] == 'xxxx':
                return redirect(url_for('address_search.address_not_found', address_input=request.args.get('input')))
            else:
                return redirect(url_for('uprn_list', uprn=request.form['form-pick-address']))
        else:
            flash('Select an address', 'error_selection')
            return redirect(url_for('address_search.addresses_by_input', input=request.args.get('input')))
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

            return render_template('address-search/address-results.html',
                                   page_title=page_title,
                                   results=address_content,
                                   error_selection=error_selection)
        else:
            return render_template('errors/500.html')


@address_search_bp.route('/addresses/postcode/', methods=['GET', 'POST'])
async def postcode_input():
    if request.method == 'POST':
        postcode_unvalidated = request.form['form_postcode_input']
        try:
            postcode = ProcessPostcode.validate_postcode(postcode_unvalidated)
            return redirect(url_for('address_search.addresses_by_postcode', postcode=postcode))
        except InvalidDataError as exc:
            current_app.logger.info(exc)
            flash(exc.message, 'error_mobile')
            return redirect(url_for('address_search.postcode_input',
                                    value_postcode=postcode_unvalidated))
    else:
        page_title = 'Enter a postcode'
        error_postcode = {}
        value_postcode = ''
        if get_flashed_messages():
            page_title = Common.page_title_error_prefix + page_title
            for message in get_flashed_messages():
                error_postcode = {'id': 'error_postcode', 'text': message}
                value_postcode = request.args.get('value_postcode')
        return render_template('address-search/postcode-input.html',
                               page_title=page_title,
                               error_postcode=error_postcode,
                               value_postcode=value_postcode)


@address_search_bp.route('/addresses/postcode/<postcode>', methods=['GET', 'POST'])
async def addresses_by_postcode(postcode):
    if request.method == 'POST':
        if 'form-pick-address' in request.form:
            if request.form['form-pick-address'] == 'xxxx':
                return redirect(url_for('address_search.address_not_found', postcode=postcode))
            else:
                return redirect(url_for('uprn_list', uprn=request.form['form-pick-address']))
        else:
            flash('Select an address', 'error_selection')
            return redirect(url_for('address_search.addresses_by_postcode', postcode=postcode))
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

            return render_template('address-search/postcode-results.html',
                                   page_title=page_title,
                                   results=address_content,
                                   error_selection=error_selection)
        else:
            return render_template('errors/500.html')


@address_search_bp.route('/addresses/address-not-found', methods=['GET'])
async def address_not_found():
    page_title = 'Address not found'
    return render_template('address-search/address-not-found.html',
                           page_title=page_title,
                           postcode=request.args.get('postcode'),
                           address_input=request.args.get('address_input'))
