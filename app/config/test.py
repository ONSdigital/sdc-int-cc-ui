"""FLASK TEST CONFIG"""
import os
import redis

TESTING = True

if not (SECRET_KEY := os.getenv('SECRET_KEY', 'testkey')):
    raise RuntimeError('no SECRET_KEY ENV variable set')

if not (CC_SVC_URL := os.getenv('CCSVC_URL', 'http://localhost')):
    raise RuntimeError('no CCSVC_URL ENV variable set')

if not (CC_SVC_USERNAME := os.getenv('CCSVC_USERNAME', 'user')):
    raise RuntimeError('no CCSVC_USERNAME ENV variable set')

if not (CC_SVC_PWD := os.getenv('CCSVC_PASSWORD', 'password')):
    raise RuntimeError('no CCSVC_PASSWORD ENV variable set')

if not (REDIS_SERVER := os.getenv('REDIS_SERVER', 'localhost')):
    raise RuntimeError('no REDIS_SERVER ENV variable set')

if not (REDIS_PORT := os.getenv('REDIS_PORT', '6379')):
    raise RuntimeError('no REDIS_PORT ENV variable set')

SESSION_REDIS = redis.Redis(host=REDIS_SERVER, port=REDIS_PORT, retry_on_timeout=True)
