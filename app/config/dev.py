"""FLASK DEVELOPMENT CONFIG"""
import os

SECRET_KEY = b'secretkey'
FLASK_DEBUG = 0

if not (CC_SVC_URL := os.getenv('CCSVC_URL', 'http://localhost:8171')):
    raise RuntimeError('no CCSVC_URL ENV variable set')

if not (CC_SVC_USERNAME := os.getenv('CCSVC_USERNAME', 'user')):
    raise RuntimeError('no CCSVC_USERNAME ENV variable set')

if not (CC_SVC_PWD := os.getenv('CCSVC_PASSWORD', 'password')):
    raise RuntimeError('no CCSVC_PASSWORD ENV variable set')
