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
            logger.info('attributes: ' + str(attributes))
    return attributes


def get_name():
    """
    Create a "forename surname" name from the attributes
    """
    name = ''
    attributes = get_attributes()
    if attributes:
        forename_key = 'givenname'
        surname_key = 'surname'
        if current_app.config['ADFS'] == 'True':
            claim_prefix = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/'
            forename_key = claim_prefix + forename_key
            surname_key = claim_prefix + surname_key

        forename = session['samlUserdata'].get(forename_key, [None])[0]
        surname = session['samlUserdata'].get(surname_key, [None])[0]
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
