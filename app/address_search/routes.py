from . import address_search_bp
from app import app
from flask import render_template, request, redirect, url_for
from app.utils import CCSvc, ProcessPostcode


@address_search_bp.route('/addresses/', methods=['GET', 'POST'])
async def address_input():
    if request.method == 'POST':
        return redirect(url_for('address_search.addresses_by_input', input=request.form['form_address_input']))
    else:
        return render_template('address-search/address-input.html')


@address_search_bp.route('/addresses/input/', methods=['GET', 'POST'])
async def addresses_by_input():
    if request.method == 'POST':
        return redirect(url_for('uprn_list', uprn=request.form['form-pick-address']))
    else:
        if request.args.get('input'):
            app.logger.info('Starting')
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

            return render_template('address-search/address-results.html', results=address_content)
        else:
            return render_template('500.html')


@address_search_bp.route('/addresses/postcode/', methods=['GET', 'POST'])
async def postcode_input():
    if request.method == 'POST':
        postcode_return = ProcessPostcode.validate_postcode(request.form['form_postcode_input'])
        if postcode_return['valid'] == 'true':
            return redirect(url_for('address_search.addresses_by_postcode', postcode=postcode_return['postcode']))
        else:
            return render_template('address-search/postcode-input.html',
                                   postcode_value=postcode_return['postcode'],
                                   error_message=postcode_return['error_message'])
    else:
        return render_template('address-search/postcode-input.html')


@address_search_bp.route('/addresses/postcode/<postcode>', methods=['GET', 'POST'])
async def addresses_by_postcode(postcode):
    if request.method == 'POST':
        return redirect(url_for('uprn_list', uprn=request.form['form-pick-address']))
    else:
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

            return render_template('address-search/postcode-results.html', results=address_content)
        else:
            return render_template('500.html')
