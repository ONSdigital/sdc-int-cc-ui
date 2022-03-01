import os

from pathlib import Path
from structlog import get_logger
from redis import Redis

logger = get_logger()


def read_file(file_name):
    if file_name and os.path.isfile(file_name):
        logger.debug("reading from file", filename=file_name)
        with open(file_name, "r") as file:
            contents = file.read()
            return contents
    else:
        logger.info(
            "Did not load file because filename supplied was None or not a file",
            filename=file_name,
        )
        return None


def get_env_or_fail(key):
    value = os.getenv(key)
    if value is None:
        raise Exception(f"Setting '{key}' Missing")

    return value


APPLICATION_VERSION_PATH = ".application-version"
APPLICATION_VERSION = read_file(APPLICATION_VERSION_PATH)
FLASK_ENV = os.getenv("FLASK_ENV", "production")

CDN_URL = os.getenv("CDN_URL", "https://cdn.ons.gov.uk")
CDN_ASSETS_PATH = os.getenv("CDN_ASSETS_PATH", "/sdc/design-system")

if FLASK_ENV == "production":
    REDIS_SERVER = get_env_or_fail("REDIS_SERVER")
    REDIS_PORT = get_env_or_fail("REDIS_PORT")
    ENABLE_SECURE_SESSION_COOKIE = get_env_or_fail('ENABLE_SECURE_SESSION_COOKIE')
    SECRET_KEY = get_env_or_fail('SECRET_KEY')
    CCSVC_URL = get_env_or_fail('CCSVC_URL')
else:
    REDIS_SERVER = os.getenv("REDIS_SERVER", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    ENABLE_SECURE_SESSION_COOKIE = os.getenv('ENABLE_SECURE_SESSION_COOKIE', 'False')
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret_key')
    CCSVC_URL = os.getenv('CCSVC_URL', 'http://localhost:8171/ccsvc')

SESSION_TYPE = 'redis'
SESSION_PERMANENT = True
SESSION_USE_SIGNER = True
SESSION_COOKIE_NAME = 'ons_cc'
SESSION_TIMEOUT_SECS = 2700
SESSION_REDIS = Redis(host=REDIS_SERVER, port=REDIS_PORT, retry_on_timeout=True)
SAML_PATH = os.getenv('SAML_PATH', str(Path(__file__).resolve().parent.parent / 'saml'))
ADFS = os.getenv('SAML_ADFS', 'False')

logger.info('SAML_PATH: ' + SAML_PATH)
logger.info('ADFS: ' + ADFS)
