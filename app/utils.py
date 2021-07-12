import requests
import string
import re

from flask import current_app, flash
from unicodedata import normalize

OBSCURE_WHITESPACE = (
    '\u180E'  # Mongolian vowel separator
    '\u200B'  # zero width space
    '\u200C'  # zero width non-joiner
    '\u200D'  # zero width joiner
    '\u2060'  # word joiner
    '\uFEFF'  # zero width non-breaking space
)

# class Utils:
    # Common classes


class ProcessPostcode:
    postcode_validation_pattern = re.compile(
        r'^((AB|AL|B|BA|BB|BD|BH|BL|BN|BR|BS|BT|BX|CA|CB|CF|CH|CM|CO|CR|CT|CV|CW|DA|DD|DE|DG|DH|DL|DN|DT|DY|E|EC|EH|EN|EX|FK|FY|G|GL|GY|GU|HA|HD|HG|HP|HR|HS|HU|HX|IG|IM|IP|IV|JE|KA|KT|KW|KY|L|LA|LD|LE|LL|LN|LS|LU|M|ME|MK|ML|N|NE|NG|NN|NP|NR|NW|OL|OX|PA|PE|PH|PL|PO|PR|RG|RH|RM|S|SA|SE|SG|SK|SL|SM|SN|SO|SP|SR|SS|ST|SW|SY|TA|TD|TF|TN|TQ|TR|TS|TW|UB|W|WA|WC|WD|WF|WN|WR|WS|WV|YO|ZE)(\d[\dA-Z]?[ ]?\d[ABD-HJLN-UW-Z]{2}))$'  # NOQA
    )

    @staticmethod
    def validate_postcode(postcode):

        for character in string.whitespace + OBSCURE_WHITESPACE:
            postcode = postcode.replace(character, '')

        postcode = postcode.upper()
        postcode = normalize('NFKD', postcode).encode('ascii', 'ignore').decode('utf8')
        postcode_valid = 'true'
        error_message = ''

        if len(postcode) == 0:
            flash('Enter a postcode', 'error_postcode')
            error_message = 'Enter a postcode'
            postcode_valid = 'false'
        elif not postcode.isalnum():
            flash('Postcode can only contain letters and numbers', 'error_postcode')
            error_message = 'Postcode can only contain letters and numbers'
            postcode_valid = 'false'
        else:
            if len(postcode) < 5:
                flash('Postcode is too short', 'error_postcode')
                error_message = 'Postcode is too short'
                postcode_valid = 'false'
            elif len(postcode) > 7:
                flash('Postcode is too long', 'error_postcode')
                error_message = 'Postcode is too long'
                postcode_valid = 'false'
            elif not ProcessPostcode.postcode_validation_pattern.fullmatch(postcode):
                flash('Enter a valid UK postcode', 'error_postcode')
                error_message = 'Enter a valid UK postcode'
                postcode_valid = 'false'

        if postcode_valid:
            postcode = postcode[:-3] + ' ' + postcode[-3:]

        return {'valid': postcode_valid, 'postcode': postcode, 'error_message': error_message}


class CCSvc:
    @staticmethod
    async def get_case_by_id(case):
        cc_svc_url = current_app.config['CC_SVC_URL']
        url = f'{cc_svc_url}/cases/{case}'

        try:
            cc_return = requests.get(url, auth=(current_app.config['CC_SVC_USERNAME'],
                                                current_app.config['CC_SVC_PWD']))
            cc_return.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

        return cc_return.json()

    @staticmethod
    async def get_case_by_uprn(uprn):
        cc_svc_url = current_app.config['CC_SVC_URL']
        url = f'{cc_svc_url}/cases/uprn/{uprn}'

        try:
            cc_return = requests.get(url, auth=(current_app.config['CC_SVC_USERNAME'],
                                                current_app.config['CC_SVC_PWD']))
            cc_return.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

        return cc_return.json()

    @staticmethod
    async def get_addresses_by_postcode(postcode):
        cc_svc_url = current_app.config['CC_SVC_URL']
        url = f'{cc_svc_url}/addresses/postcode'
        params = {'postcode': postcode, 'limit': 5000}
        try:
            cc_return = requests.get(url, params=params, auth=(current_app.config['CC_SVC_USERNAME'],
                                                               current_app.config['CC_SVC_PWD']))
            cc_return.raise_for_status()
        except requests.exceptions.HTTPError as err:
            current_app.logger.info(err)
            raise SystemExit(err)

        return cc_return.json()

    @staticmethod
    async def get_addresses_by_input(input_text):
        cc_svc_url = current_app.config['CC_SVC_URL']
        url = f'{cc_svc_url}/addresses'
        params = {'input': input_text}
        current_app.logger.info('Trying ' + input_text)
        try:
            cc_return = requests.get(url, params=params, auth=(current_app.config['CC_SVC_USERNAME'],
                                                               current_app.config['CC_SVC_PWD']))
            cc_return.raise_for_status()
        except requests.exceptions.HTTPError as err:
            current_app.logger.info('Call Error')
            raise SystemExit(err)

        return cc_return.json()
