"""FLASK TEST CONFIG"""
import os

TESTING = True
CCSVC_PREFIX = '/ccsvc'

if not (SECRET_KEY := os.getenv('SECRET_KEY', 'testkey')):
    raise RuntimeError('no SECRET_KEY ENV variable set')

if not (CC_SVC_URL := os.getenv('CCSVC_URL', 'http://localhost') + CCSVC_PREFIX):
    raise RuntimeError('no CCSVC_URL ENV variable set')

if not (CC_SVC_USERNAME := os.getenv('CCSVC_USERNAME', 'user')):
    raise RuntimeError('no CCSVC_USERNAME ENV variable set')

if not (CC_SVC_PWD := os.getenv('CCSVC_PASSWORD', 'password')):
    raise RuntimeError('no CCSVC_PASSWORD ENV variable set')
