"""FLASK PROD CONFIG"""
import os

if not (SECRET_KEY := os.getenv('SECRET_KEY')):
    raise RuntimeError('no SECRET_KEY ENV variable set')

if not (CC_SVC_URL := os.getenv('CC_SVC_URL')):
    raise RuntimeError('no CC_SVC_URL ENV variable set')

if not (CC_SVC_USERNAME := os.getenv('CC_SVC_USERNAME')):
    raise RuntimeError('no CC_SVC_USERNAME ENV variable set')

if not (CC_SVC_PWD := os.getenv('CC_SVC_PWD')):
    raise RuntimeError('no CC_SVC_PWD ENV variable set')
