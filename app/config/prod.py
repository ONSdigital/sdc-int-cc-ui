"""FLASK PROD CONFIG"""
import os
import redis

if not (SECRET_KEY := os.getenv('SECRET_KEY')):
    raise RuntimeError('no SECRET_KEY ENV variable set')

if not (CC_SVC_URL := os.getenv('CCSVC_URL')):
    raise RuntimeError('no CCSVC_URL ENV variable set')

if not (CC_SVC_USERNAME := os.getenv('CCSVC_USERNAME')):
    raise RuntimeError('no CCSVC_USERNAME ENV variable set')

if not (CC_SVC_PWD := os.getenv('CCSVC_PASSWORD')):
    raise RuntimeError('no CCSVC_PASSWORD ENV variable set')

if not (PERMANENT_SESSION_LIFETIME := os.getenv('SESSION_AGE')):
    raise RuntimeError('no SESSION_AGE ENV variable set')

if not (REDIS_SERVER := os.getenv('REDIS_SERVER')):
    raise RuntimeError('no REDIS_SERVER ENV variable set')

if not (REDIS_PORT := os.getenv('REDIS_PORT')):
    raise RuntimeError('no REDIS_PORT ENV variable set')

SESSION_REDIS = redis.from_url('redis://' + REDIS_SERVER + ':' + REDIS_PORT)
