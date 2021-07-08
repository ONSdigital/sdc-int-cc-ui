from app import app
from flask import render_template, request, redirect, url_for, current_app
from .utils import CCSvc


@app.route('/ccui/')
async def home():
    return render_template('home.html')


@app.route('/ccui/case/<case_id>', methods=['GET'])
async def case(case_id):
    if case_id:
        cc_return = await CCSvc.get_case_by_id(case_id)

        return render_template('case.html', case=cc_return)
    else:
        return render_template('error.html')


@app.route('/ccui/uprn/<uprn>', methods=['GET'])
async def uprn_list(uprn):
    if uprn:
        cc_return = await CCSvc.get_case_by_uprn(uprn)
        case_list = []
        for single_case in cc_return:
            case_list.append({'text': single_case['id'], 'url': url_for('case', case_id=single_case['id'])})

        address_output = ''
        address_output = address_output + cc_return[0]['addressLine1']
        if cc_return[0]['addressLine2']:
            address_output = address_output + ', ' + cc_return[0]['addressLine2']
        if cc_return[0]['addressLine3']:
            address_output = address_output + ', ' + cc_return[0]['addressLine3']
        if cc_return[0]['townName']:
            address_output = address_output + ', ' + cc_return[0]['townName']
        if cc_return[0]['postcode']:
            address_output = address_output + ', ' + cc_return[0]['postcode']

        return render_template('uprn-list.html', uprn=uprn, address_output=address_output, case_list=case_list)
    else:
        return render_template('error.html')


@app.route('/ccui/addresses/', methods=['GET', 'POST'])
async def address_input():
    if request.method == 'POST':
        return redirect(url_for('addresses_by_input', input=request.form['form_address_input']))
    else:
        return render_template('address-input.html')


@app.route('/ccui/addresses/input/', methods=['GET', 'POST'])
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

            return render_template('address-results.html', results=address_content)
        else:
            return render_template('error.html')


@app.route('/ccui/addresses/postcode/', methods=['GET', 'POST'])
async def postcode_input():
    if request.method == 'POST':
        return redirect(url_for('addresses_by_postcode', postcode=request.form['form_postcode_input']))
    else:
        return render_template('postcode-input.html')


@app.route('/ccui/addresses/postcode/<postcode>', methods=['GET', 'POST'])
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

            return render_template('postcode-results.html', results=address_content)
        else:
            return render_template('error.html')
