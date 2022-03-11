import requests

from flask import current_app, abort, json
from app.user_context import get_logged_in_user
from app.routes.errors import Case404, UserExistsAlready
from datetime import datetime
from pytz import utc
from structlog import get_logger

logger = get_logger()


class CCSvc:
    """
    Enable calls to CCSvc backend
    """

    def __init__(self):
        self.__svc_url = current_app.config['CCSVC_URL']
        self.__user_logged_in = get_logged_in_user()
        self.__headers = {"x-user-id": self.__user_logged_in}
        pass

    def _get_response(self, url, params=None):
        return requests.get(url, params=params, headers=self.__headers)

    def _get(self, url, check404, description, params=None):
        try:
            cc_return = self._get_response(url, params)
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

    def _post(self, url, payload, description):
        try:
            cc_return = requests.post(url, headers=self.__headers, json=payload)
            cc_return.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.warn('Error returned by CCSvc for ' + description + ': ' + str(err))
            raise abort(500)
        except requests.exceptions.ConnectionError:
            logger.warn('Error: Unable to connect to CCSvc')
            raise abort(500)

        return cc_return.json()

    def _put(self, url, payload, description, json_response=True, ignore_401=False):
        try:
            cc_return = requests.put(url, headers=self.__headers, json=payload)
            cc_return.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if ignore_401 and err.response.status_code == 401:
                return
            logger.warn('Error returned by CCSvc for ' + description + ': ' + str(err))
            raise abort(500)
        except requests.exceptions.ConnectionError:
            logger.warn('Error: Unable to connect to CCSvc')
            raise abort(500)
        if json_response:
            return cc_return.json()

    def _delete(self, url, description):
        try:
            cc_return = requests.delete(url, headers=self.__headers)
            cc_return.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.warn('Error returned by CCSvc for ' + description + ': ' + str(err))
            raise abort(500)
        except requests.exceptions.ConnectionError:
            logger.warn('Error: Unable to connect to CCSvc')
            raise abort(500)

    def get_permissions(self):
        url = f'{self.__svc_url}/users/permissions'
        resp = self._get_response(url)
        perms = resp.json() if resp.ok else json.loads('[]')
        logger.info('User: ' + self.__user_logged_in + ' has these permissions: ' + str(perms))
        return perms

    def login(self, forename, surname):
        url = f'{self.__svc_url}/users/login'
        login_json = {
            'forename': forename,
            'surname': surname
        }
        # if the user hasn't been setup yet, we allow 401 so we can display tailored message
        return self._put(url, login_json, 'login', json_response=True, ignore_401=True)

    def logout(self, user_logging_out):
        self.__headers["x-user-id"] = user_logging_out
        url = f'{self.__svc_url}/users/logout'
        # if the user hasn't been setup yet, we allow 401 so we can display tailored message
        return self._put(url, None, 'logout', json_response=False, ignore_401=True)

    @staticmethod
    def err_match(err, response, code, message):
        match = False
        if err.response.status_code == code:
            err_json = response.json()
            if 'error' in err_json:
                err_msg = err_json['error']['message']
                return err_msg == message
        return match

    async def add_user(self, user_identity):
        url = f'{self.__svc_url}/users'
        create_json = {
            'identity': user_identity
        }
        try:
            cc_return = requests.post(url, headers=self.__headers, json=create_json)
            cc_return.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.warn('Error returned by CCSvc when creating user: ' + str(err))
            if CCSvc.err_match(err, cc_return, 400, 'User with that name already exists'):
                raise UserExistsAlready
            else:
                raise abort(500)
        except requests.exceptions.ConnectionError:
            logger.warn('Error: Unable to connect to CCSvc')
            raise abort(500)

        return cc_return.json()

    async def modify_user(self, user_identity, active):
        url = f'{self.__svc_url}/users/{user_identity}'
        modify_json = {
            'active': active
        }
        self._put(url, modify_json, 'modify user', json_response=False)

    async def delete_user(self, user_identity):
        url = f'{self.__svc_url}/users/{user_identity}'
        self._delete(url, 'delete user')

    async def get_user(self, user_identity):
        url = f'{self.__svc_url}/users/{user_identity}'
        return self._get(url, False, 'get user')

    async def get_case_by_id(self, case, case_events=False):
        url = f'{self.__svc_url}/cases/{case}?caseEvents={case_events}'
        return self._get(url, True, 'get_case_by_id')

    async def post_add_note(self, case_id, note):
        url = f'{self.__svc_url}/cases/{case_id}/interaction'
        interaction_json = {
            'caseId': case_id,
            'type': 'CASE_NOTE_ADDED',
            'note': note
        }
        return self._post(url, interaction_json, 'post_add_note')

    async def post_case_refusal(self, case_id, reason, note=None, erase_data=False):
        url = f'{self.__svc_url}/cases/{case_id}/refusal'
        refusal_json = {
            'caseId': case_id,
            'reason': reason,
            'note': note,
            'eraseData': erase_data
        }
        return self._post(url, refusal_json, 'case refusal')

    async def get_addresses_by_postcode(self, postcode):
        url = f'{self.__svc_url}/addresses/postcode'
        params = {'postcode': postcode, 'limit': 5000}
        return self._get(url, False, 'addresses by postcode', params)

    async def get_addresses_by_input(self, input_text):
        url = f'{self.__svc_url}/addresses'
        params = {'input': input_text}
        logger.info('Trying ' + input_text)
        return self._get(url, False, 'addresses by input', params)

    async def get_users(self):
        url = f'{self.__svc_url}/users'
        return self._get(url, False, 'all users')

    async def get_survey_types(self):
        url = f'{self.__svc_url}/surveys/usages'
        usages = self._get(url, False, 'survey types')
        return [i['surveyType'] for i in usages]

    async def get_roles(self):
        url = f'{self.__svc_url}/roles'
        return self._get(url, False, 'roles')

    async def add_user_survey(self, user_identity, survey_type):
        url = f'{self.__svc_url}/users/{user_identity}/addSurvey/{survey_type}'
        requests.patch(url, headers=self.__headers)

    async def remove_user_survey(self, user_identity, survey_type):
        url = f'{self.__svc_url}/users/{user_identity}/removeSurvey/{survey_type}'
        requests.patch(url, headers=self.__headers)

    async def add_user_role(self, user_identity, role):
        url = f'{self.__svc_url}/users/{user_identity}/addUserRole/{role}'
        requests.patch(url, headers=self.__headers)

    async def remove_user_role(self, user_identity, role):
        url = f'{self.__svc_url}/users/{user_identity}/removeUserRole/{role}'
        requests.patch(url, headers=self.__headers)

    async def add_admin_role(self, user_identity, role):
        url = f'{self.__svc_url}/users/{user_identity}/addAdminRole/{role}'
        requests.patch(url, headers=self.__headers)

    async def remove_admin_role(self, user_identity, role):
        url = f'{self.__svc_url}/users/{user_identity}/removeAdminRole/{role}'
        requests.patch(url, headers=self.__headers)

    async def get_fulfilments(self, product_group, delivery_channel, region):
        url = f'{self.__svc_url}/fulfilments'
        params = {
            'caseType': 'HH',
            'productGroup': product_group,
            'deliveryChannel': delivery_channel,
            'region': region,
            'individual': 'false'
        }
        return self._get(url, False, 'get fulfilments', params)

    async def post_sms_fulfilment(self, case_id, fulfilment_code, tel_no):
        url = f'{self.__svc_url}/cases/{case_id}/fulfilment/sms'
        fulfilment_json = {
            'caseId': case_id,
            'dateTime': datetime.now(utc).isoformat(),
            'fulfilmentCode': fulfilment_code,
            'telNo': tel_no
        }
        return self._post(url, fulfilment_json, 'SMS fulfilment')

    async def post_postal_fulfilment(self, case_id, fulfilment_code, first_name, last_name):
        url = f'{self.__svc_url}/cases/{case_id}/fulfilment/post'
        fulfilment_json = {
            'caseId': case_id,
            'dateTime': datetime.now(utc).isoformat(),
            'fulfilmentCode': fulfilment_code,
            'forename': first_name,
            'surname': last_name
        }
        return self._post(url, fulfilment_json, 'postal fulfilment')
