import os

from flask import Flask
from flask import request
from .config import base as config_base
from flask_session import Session
from datetime import datetime

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


@app.template_filter()
def datetimefilter(value, in_format='%Y-%m-%dT%H:%M:%S.%f%z'):
    return datetime.strptime(value, in_format).strftime('%d %B %Y, %X')


app.jinja_env.filters['datetimefilter'] = datetimefilter

from . import routes
# from . import errors
