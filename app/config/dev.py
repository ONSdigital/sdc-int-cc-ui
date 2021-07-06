"""FLASK DEVELOPMENT CONFIG"""
import os

SECRET_KEY = b'secretkey'
FLASK_DEBUG = 0

if not (CC_SVC_URL := os.getenv('CC_SVC_URL', 'http://localhost')):
    raise RuntimeError('no CC_SVC_URL ENV variable set')

if not (CC_SVC_USERNAME := os.getenv('CC_SVC_USERNAME', 'user')):
    raise RuntimeError('no CC_SVC_USERNAME ENV variable set')

if not (CC_SVC_PWD := os.getenv('CC_SVC_PWD', 'password')):
    raise RuntimeError('no CC_SVC_PWD ENV variable set')
