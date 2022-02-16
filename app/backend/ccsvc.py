import requests

from flask import current_app, abort, json
from app.user_auth import get_logged_in_user
from app.routes.errors import Case404
from datetime import datetime
from pytz import utc
from structlog import get_logger

logger = get_logger()


class CCSvc:
    """
    Enable calls to CCSvc backend
    """

    def __init__(self):
        self.__username = current_app.config['CCSVC_USERNAME']
        self.__password = current_app.config['CCSVC_PASSWORD']
        self.__creds = (self.__username, self.__password)
        self.__svc_url = current_app.config['CCSVC_URL']
        self.__user_logged_in = get_logged_in_user()
        pass

    def __get_response(self, url, params=None):
        return requests.get(url, auth=self.__creds,
                            params=params,
                            headers={"x-user-id": self.__user_logged_in})

    def __get(self, url, check404, description, params=None):
        try:
            cc_return = self.__get_response(url, params)
            cc_return.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.warn('Error returned by CCSvc for ' + description + ': ' + str(err.response))
            if check404 and err.response.status_code == 404:
                logger.warn('404: No matching case')
                raise Case404
            else:
                raise abort(500)
        except requests.exceptions.ConnectionError:
            logger.warn('Error: Unable to connect to CCSvc')
            raise abort(500)

        return cc_return.json()

    def __post(self, url, payload, description):
        try:
            cc_return = requests.post(url, auth=self.__creds,
                                      headers={"x-user-id": self.__user_logged_in},
                                      json=payload)
            cc_return.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.warn('Error returned by CCSvc for ' + description + ': ' + str(err))
            raise abort(500)
        except requests.exceptions.ConnectionError:
            logger.warn('Error: Unable to connect to CCSvc')
            raise abort(500)

        return cc_return.json()

    async def get_permissions(self):
        url = f'{self.__svc_url}/users/permissions'
        resp = self.__get_response(url)
        perms = resp.json() if resp.ok else json.loads('[]')
        logger.info('User: ' + self.__user_logged_in + ' has these permissions: ' + str(perms))
        return perms

    async def get_case_by_id(self, case, case_events=False):
        url = f'{self.__svc_url}/cases/{case}?caseEvents={case_events}'
        return self.__get(url, True, 'get_case_by_id')

    async def post_add_note(self, case_id, note):
        url = f'{self.__svc_url}/cases/{case_id}/interaction'
        interaction_json = {
            'caseId': case_id,
            'type': 'CASE_NOTE_ADDED',
            'note': note
        }
        return self.__post(url, interaction_json, 'post_add_note')

    async def post_case_refusal(self, case_id, reason):
        url = f'{self.__svc_url}/cases/{case_id}/refusal'
        refusal_json = {
            'caseId': case_id,
            'dateTime': datetime.now(utc).isoformat(),
            'reason': reason
        }
        return self.__post(url, refusal_json, 'case refusal')

    async def get_addresses_by_postcode(self, postcode):
        url = f'{self.__svc_url}/addresses/postcode'
        params = {'postcode': postcode, 'limit': 5000}
        return self.__get(url, False, 'addresses by postcode', params)

    async def get_addresses_by_input(self, input_text):
        url = f'{self.__svc_url}/addresses'
        params = {'input': input_text}
        logger.info('Trying ' + input_text)
        return self.__get(url, False, 'addresses by input', params)

    async def get_fulfilments(self, product_group, delivery_channel, region):
        url = f'{self.__svc_url}/fulfilments'
        params = {
            'caseType': 'HH',
            'productGroup': product_group,
            'deliveryChannel': delivery_channel,
            'region': region,
            'individual': 'false'
        }
        return self.__get(url, False, 'get fulfilments', params)

    async def post_sms_fulfilment(self, case_id, fulfilment_code, tel_no):
        url = f'{self.__svc_url}/cases/{case_id}/fulfilment/sms'
        fulfilment_json = {
            'caseId': case_id,
            'dateTime': datetime.now(utc).isoformat(),
            'fulfilmentCode': fulfilment_code,
            'telNo': tel_no
        }
        return self.__post(url, fulfilment_json, 'SMS fulfilment')

    async def post_postal_fulfilment(self, case_id, fulfilment_code, first_name, last_name):
        url = f'{self.__svc_url}/cases/{case_id}/fulfilment/post'
        fulfilment_json = {
            'caseId': case_id,
            'dateTime': datetime.now(utc).isoformat(),
            'fulfilmentCode': fulfilment_code,
            'forename': first_name,
            'surname': last_name
        }
        return self.__post(url, fulfilment_json, 'postal fulfilment')
