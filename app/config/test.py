"""FLASK TEST CONFIG"""
import os

if not (SECRET_KEY := os.getenv('SECRET_KEY')):
    raise RuntimeError('no SECRET_KEY ENV variable set')

if not (CC_SVC_URL := os.getenv('CCSVC_URL')):
    raise RuntimeError('no CCSVC_URL ENV variable set')

if not (CC_SVC_USERNAME := os.getenv('CCSVC_USERNAME')):
    raise RuntimeError('no CCSVC_USERNAME ENV variable set')

if not (CC_SVC_PWD := os.getenv('CCSVC_PASSWORD')):
    raise RuntimeError('no CCSVC_PASSWORD ENV variable set')
