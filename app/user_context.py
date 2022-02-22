from flask import session, current_app
from structlog import get_logger

logger = get_logger()


"""
Functions for getting or setting the user details in the session.
"""


def get_logged_in_user():
    return session.get('samlNameId', 'nobody')


def is_logged_in():
    return 'samlNameId' in session and len(session['samlNameId']) > 0


def get_attributes():
    """
    get the attributes dictionary from the session that was stored when we logged in.
    """
    attributes = None
    if 'samlUserdata' in session:
        if len(session['samlUserdata']) > 0:
            attributes = session['samlUserdata']
    return attributes


def _get_name(base_key):
    """
    Get name from the attributes, given by key
    """
    name = ''
    key = base_key
    attributes = get_attributes()
    if attributes:
        if current_app.config['ADFS'] == 'True':
            claim_prefix = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/'
            key = claim_prefix + base_key
        name = session['samlUserdata'].get(key, [None])[0]
    return name


def get_forename():
    return _get_name('givenname')


def get_surname():
    return _get_name('surname')


def get_name():
    """
    Create a "forename surname" name from the attributes
    """
    name = ''
    forename = get_forename()
    surname = get_surname()
    if forename:
        name = forename
    if surname:
        name = name + ' ' + surname
    return name


def setup_user_context_utilities(application):
    """
    Set up utility methods that can be called from the jinja2 HTML templates.
    """
    @application.context_processor
    def utility_processor():
        return dict(get_id=get_logged_in_user, is_logged_in=is_logged_in)
