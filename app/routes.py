from app import app
from flask import render_template, url_for
from .utils import CCSvc


@app.route('/')
async def home():
    return render_template('home.html')


@app.route('/uprn/<uprn>', methods=['GET'])
async def uprn_list(uprn):
    if uprn:
        cc_return = await CCSvc.get_case_by_uprn(uprn)
        case_list = []
        for single_case in cc_return:
            case_list.append({'text': 'Census 2021: Household', 'url': url_for('case.case', case_id=single_case['id'])})

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

        return render_template('uprn-list.html', uprn=uprn, address_output=address_output, case_list=case_list)
    else:
        return render_template('500.html')
