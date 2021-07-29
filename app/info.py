import os
from . import app
from flask import jsonify
from importlib_metadata import version, PackageNotFoundError


def get_version():
    try:
        return version('cc_ui')
    except PackageNotFoundError as e:
        app.logger.warning(
            'Unable to determine cc_ui version, cc_ui was not installed as a package'
        )
        return 'Unknown'


@app.route('/info')
def info():
    key_info = {'ENV': os.getenv('FLASK_ENV'), 'PLATFORM': os.getenv('PLATFORM'), 'VERSION': get_version()}

    return jsonify(key_info)
