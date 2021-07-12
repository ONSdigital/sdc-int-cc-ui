import requests

from flask import current_app


# class Utils:
    # Common classes


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
