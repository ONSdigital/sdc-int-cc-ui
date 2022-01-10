from flask import render_template, request, url_for, flash, current_app
from app.utils import CCSvc
from flask import Blueprint
import re

sel_bp = Blueprint('sel', __name__)


def highlight_term(addr, addr_input, hi_start, hi_end):
    """
    Highlight the term searched.
    Do some work to make this space insensitive.
    """
    if not addr_input:
        return addr

    highlighted = addr
    condensed_addr = re.sub(r"\s+", "", addr)
    condensed_input = re.sub(r"\s+", "", addr_input)

    mapping = {}
    index = 0
    for i, v in enumerate(addr):
        if not v.isspace():
            mapping[index] = i
            index = index + 1

    match = re.search(condensed_input, condensed_addr)
    if match:
        start = mapping.get(match.start(), 0)
        end = mapping.get(match.end(), len(addr))
        while addr[end - 1].isspace():
            end = end - 1
        highlighted = addr[:start] + hi_start + addr[start:end] + hi_end + addr[end:]
    return highlighted


def is_address_input_valid(addr_input):
    """
    Ensure input term is valid for lookup
    """
    stripped_input = addr_input.replace("'", '').replace(',', '').strip()
    return len(stripped_input) >= 5


def build_address_results(addr_input, cc_return):
    results = []
    for address in cc_return['addresses']:
        surveys = ''
        case_refs = ''
        for caze in address['cases']:
            surveys = surveys + caze['surveyName'] + '<br/>'
            case_link = '<a href="' + url_for('case.case', case_id=caze['id'], org='sel') \
                        + '">' + caze['caseRef'] + '</a>'
            case_refs = case_refs + case_link + '<br/>'

        addr = highlight_term(address['formattedAddress'], addr_input, '<b>', '<b/>')

        results.append({
            'tds': [
                {
                    'value': addr
                },
                {
                    'value': surveys
                },
                {
                    'value': case_refs
                }
            ]
        })
    return results


@sel_bp.route('/sel/', methods=['GET', 'POST'])
async def sel_home():
    if request.method == 'POST':
        addr_input = request.form['form_address_input']
        results = []
        if addr_input:
            if is_address_input_valid(addr_input):
                cc_return = await CCSvc.get_addresses_by_input(addr_input)
                results = build_address_results(addr_input, cc_return)
            else:
                current_app.logger.info('Address input error: Please supply a longer search term')
                flash('Please supply a longer search term', 'error_input')
        else:
            current_app.logger.info('Address input error: No value entered')
            flash('Enter an address value', 'error_input')

        return render_template('sel/home.html', results=results, addr_input=addr_input)
    else:
        return render_template('sel/home.html')


@sel_bp.route('/sel/uprn-not-found', methods=['GET'])
async def uprn_not_found():
    page_title = 'No cases found'
    return render_template('sel/uprn-not-found.html', page_title=page_title)


@sel_bp.route('/sel/uprn/<uprn>', methods=['GET'])
async def uprn_list(uprn):
    if uprn:
        cc_return = await CCSvc.get_cases_by_attribute('uprn', uprn)
        if cc_return:
            case_list = []
            for single_case in cc_return:
                case_list.append({'text': 'Census 2021: Household',
                                  'url': url_for('case.case', case_id=single_case['id'], org='sel')})

            address_output = ''
            sample_return = cc_return[0]['sample']
            address_output = address_output + sample_return['addressLine1']
            if sample_return['addressLine2']:
                address_output = address_output + ', ' + sample_return['addressLine2']
            if sample_return['addressLine3']:
                address_output = address_output + ', ' + sample_return['addressLine3']
            if sample_return['townName']:
                address_output = address_output + ', ' + sample_return['townName']
            if sample_return['postcode']:
                address_output = address_output + ', ' + sample_return['postcode']

            return render_template('sel/uprn-list.html', uprn=uprn, address_output=address_output, case_list=case_list)
        else:
            return render_template('sel/uprn-not-found.html')
    else:
        return render_template('errors/500.html')
