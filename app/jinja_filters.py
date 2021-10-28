from flask import Blueprint
from datetime import datetime

blueprint = Blueprint("filters", __name__)


@blueprint.app_template_filter()
def datetime_filter(value, in_format='%Y-%m-%dT%H:%M:%S.%f%z'):
    return datetime.strptime(value, in_format).strftime('%d %B %Y, %X')
