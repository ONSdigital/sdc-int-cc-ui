import os

from flask import Flask
from .config import base as config_base
from .logging import setup_logging
from flask_session import Session
from datetime import datetime

setup_logging(os.getenv('PLATFORM'))

app = Flask(__name__, instance_relative_config=False)

ENV = os.getenv('FLASK_ENV')

app.config.from_object(config_base)

if ENV == 'development':
    from .config import dev as config_env
elif ENV == 'testing':
    from .config import test as config_env
elif ENV == 'production':
    from .config import prod as config_env
else:
    raise RuntimeError('invalid environment ' + str(ENV))

app.config.from_object(config_env)

# Create and initialize the Flask-Session object AFTER `app` has been configured
server_session = Session(app)

from app.case import case_bp as case_bp
app.register_blueprint(case_bp)
from app.address_search import address_search_bp as address_search_bp
app.register_blueprint(address_search_bp)
from app.errors import errors_bp as errors_bp
app.register_blueprint(errors_bp)


@app.template_filter()
def datetimefilter(value, in_format='%Y-%m-%dT%H:%M:%S.%f%z'):
    return datetime.strptime(value, in_format).strftime('%d %B %Y, %X')


app.jinja_env.filters['datetimefilter'] = datetimefilter

from . import info
from . import routes
