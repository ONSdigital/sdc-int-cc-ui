from flask import render_template, request, redirect, url_for, flash, current_app, get_flashed_messages, session
from app.utils import CCSvc, ProcessPostcode, Common
from app.routes.errors import InvalidDataError
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


@sel_bp.route('/sel/', methods=['GET', 'POST'])
async def sel_home():
    if request.method == 'POST':
        addr_input = request.form['form_address_input']
        results = []
        if addr_input:
            cc_return = await CCSvc.get_addresses_by_input(addr_input)
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
        return render_template('sel/home2.html', results=results, addr_input=addr_input)
    else:
        return render_template('sel/home2.html')


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
