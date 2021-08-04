from flask import render_template
from . import errors_bp


class InvalidDataError(Exception):
    """ Raised when user supplies invalid data in form fields (on english language page) """
    def __init__(self, message=None, message_type=None):
        super().__init__(message or 'The supplied value is invalid')
        self.message = message
        self.message_type = message_type


class Case404(Exception):
    pass


class UPRN404(Exception):
    pass


@errors_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@errors_bp.app_errorhandler(Case404)
def case_not_found_error(error):
    return render_template('errors/404-case.html'), 404


@errors_bp.app_errorhandler(UPRN404)
def uprn_not_found_error(error):
    return render_template('errors/404-uprn.html'), 404


@errors_bp.app_errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500
