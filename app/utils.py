import string
import re
import os

from flask import current_app, json
from unicodedata2 import normalize
from app.routes.errors import InvalidDataError

OBSCURE_WHITESPACE = (
    '\u180E'  # Mongolian vowel separator
    '\u200B'  # zero width space
    '\u200C'  # zero width non-joiner
    '\u200D'  # zero width joiner
    '\u2060'  # word joiner
    '\uFEFF'  # zero width non-breaking space
)

uk_prefix = '44'


class Common:
    page_title_error_prefix = 'Error: '
    message_select_call_type = 'Select a call type'
    message_select_call_outcome = 'Select a call outcome'
    message_select_option = 'Select an option'
    message_contact_number = 'Enter a contact number'
    message_select_fulfilment = 'Select a fulfilment'
    message_enter_mobile = 'Enter a mobile number'


class ProcessJsonForOptions:
    @staticmethod
    def _options_from_data(data):
        options = []
        for option in data:
            options.append({
                'value': option['value'],
                'label': {
                    'text': option['text']
                },
                'id': option['value']
            })
        return options

    @staticmethod
    def options_from_json(filename):
        filename = os.path.join(current_app.static_folder, 'data', filename)
        with open(filename) as file:
            data = json.load(file)
            options = ProcessJsonForOptions._options_from_data(data)
        return options

    @staticmethod
    def options_from_json_object(json_obj):
        data = json.loads(json.dumps(json_obj))
        return ProcessJsonForOptions._options_from_data(data)


class ProcessMobileNumber:

    @staticmethod
    def normalise_phone_number(number):

        for character in string.whitespace + OBSCURE_WHITESPACE + '()-+':
            number = number.replace(character, '')

        try:
            list(map(int, number))
        except ValueError:
            raise InvalidDataError('Enter a UK mobile number in a valid format, for example, '
                                   '07700 900345 or +44 7700 900345', message_type='invalid')

        return number.lstrip('0')

    @staticmethod
    def validate_uk_mobile_phone_number(number):

        number = ProcessMobileNumber.normalise_phone_number(number).lstrip(uk_prefix).lstrip('0')

        if len(number) == 0:
            raise InvalidDataError("Enter the caller's mobile number", message_type='empty')

        if not number.startswith('7'):
            raise InvalidDataError('Enter a UK mobile number in a valid format, for example, '
                                   '07700 900345 or +44 7700 900345', message_type='invalid')

        if len(number) > 10:
            raise InvalidDataError('Enter a UK mobile number in a valid format, for example, '
                                   '07700 900345 or +44 7700 900345', message_type='invalid')

        if len(number) < 10:
            raise InvalidDataError('Enter a UK mobile number in a valid format, for example, '
                                   '07700 900345 or +44 7700 900345', message_type='invalid')

        return '{}{}'.format(uk_prefix, number)


class ProcessContactNumber:

    @staticmethod
    def normalise_phone_number(number):

        for character in string.whitespace + OBSCURE_WHITESPACE + '()-+':
            number = number.replace(character, '')

        try:
            list(map(int, number))
        except ValueError:
            raise InvalidDataError('Enter a UK telephone number in a valid format, for example, '
                                   '07700 900345 or +44 7700 900345', message_type='invalid')

        return number.lstrip('0')

    @staticmethod
    def validate_uk_phone_number(number):

        number = ProcessContactNumber.normalise_phone_number(number).lstrip(uk_prefix).lstrip('0')

        if len(number) == 0:
            raise InvalidDataError("Enter the caller's telephone number", message_type='empty')

        if len(number) > 10:
            raise InvalidDataError('Enter a UK telephone number in a valid format, for example, '
                                   '07700 900345 or +44 7700 900345', message_type='invalid')

        if len(number) < 9:
            raise InvalidDataError('Enter a UK telephone number in a valid format, for example, '
                                   '07700 900345 or +44 7700 900345', message_type='invalid')

        return '{}{}'.format(uk_prefix, number)


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

        if len(postcode) == 0:
            raise InvalidDataError("Enter the caller's postcode", message_type='empty')
        elif not postcode.isalnum():
            raise InvalidDataError("Postcode can only contain letters and numbers", message_type='invalid')
        else:
            if len(postcode) < 5:
                raise InvalidDataError("Postcode is too short", message_type='invalid')
            elif len(postcode) > 7:
                raise InvalidDataError("Postcode is too long", message_type='invalid')
            elif not ProcessPostcode.postcode_validation_pattern.fullmatch(postcode):
                raise InvalidDataError("Enter a valid UK postcode", message_type='invalid')

        postcode = postcode[:-3] + ' ' + postcode[-3:]

        return postcode


class ProcessEmail:
    email_validation_pattern = re.compile(r'(^[^@\s]+@[^@\s]+\.[^@\s]+$)')

    @staticmethod
    def validate_email(email):

        for character in string.whitespace + OBSCURE_WHITESPACE:
            email = email.replace(character, '')

        if not ProcessEmail.email_validation_pattern.fullmatch(email):
            raise InvalidDataError("Enter a valid email address", message_type='invalid')

        return email
