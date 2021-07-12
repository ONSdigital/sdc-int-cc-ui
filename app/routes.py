from app import app
from flask import render_template, url_for
from .utils import CCSvc


@app.route('/ccui/')
async def home():
    return render_template('home.html')


@app.route('/ccui/uprn/<uprn>', methods=['GET'])
async def uprn_list(uprn):
    if uprn:
        cc_return = await CCSvc.get_case_by_uprn(uprn)
        case_list = []
        for single_case in cc_return:
            case_list.append({'text': single_case['id'], 'url': url_for('case.case', case_id=single_case['id'])})

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
        return render_template('500.html')
