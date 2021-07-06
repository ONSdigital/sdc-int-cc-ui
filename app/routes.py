from app import app
from flask import render_template, request, redirect, url_for
from .utils import CCSvc


@app.route('/')
async def home():
    return render_template('home.html')


@app.route('/case/<uprn>', methods=['GET'])
async def case(uprn):
    if uprn:
        cc_return = await CCSvc.get_case_by_uprn(uprn)

        return render_template('case.html', case=cc_return)
    else:
        return render_template('error.html')


@app.route('/addresses/', methods=['GET', 'POST'])
async def address_input():
    if request.method == 'POST':
        return redirect(url_for('addresses_by_input', input=request.form['form_address_input']))
    else:
        return render_template('address-input.html')


@app.route('/addresses/input/', methods=['GET', 'POST'])
async def addresses_by_input():
    if request.method == 'POST':
        return redirect(url_for('case', uprn=request.form['form-pick-address']))
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

            return render_template('address-results.html', results=address_content)
        else:
            return render_template('error.html')


@app.route('/addresses/postcode/', methods=['GET', 'POST'])
async def postcode_input():
    if request.method == 'POST':
        return redirect(url_for('addresses_by_postcode', postcode=request.form['form_postcode_input']))
    else:
        return render_template('postcode-input.html')


@app.route('/addresses/postcode/<postcode>', methods=['GET', 'POST'])
async def addresses_by_postcode(postcode):
    if request.method == 'POST':
        return redirect(url_for('case', uprn=request.form['form-pick-address']))
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

            return render_template('postcode-results.html', results=address_content)
        else:
            return render_template('error.html')
