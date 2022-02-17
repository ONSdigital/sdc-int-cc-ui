
from flask import (request, render_template, redirect, session,
                   make_response, current_app, Blueprint, flash)

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from functools import wraps
from datetime import datetime
from structlog import get_logger
from user_context import get_name, is_logged_in, get_logged_in_user
from access import load_permissions


saml_bp = Blueprint('saml', __name__)

logger = get_logger()

"""
Endpoints and functions for user authentication, i.e. login and logout, using SAML
"""


@saml_bp.route('/saml/metadata/')
def get_metadata():
    """
    The entityID endpoint. Will return XML containing the SP metadata.
    """
    req = prepare_flask_request()
    auth = init_saml_auth(req)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers['Content-Type'] = 'text/xml'
    else:
        resp = make_response(', '.join(errors), 500)
    return resp


@saml_bp.route('/saml/sso')
def sso():
    """
    single sign-on from user , redirects to IDP
    """
    logger.info('Initiating login')
    auth, _ = do_auth()
    return redirect(auth.login(request.host_url))
    # If AuthNRequest ID need to be stored in order to later validate it, do instead
    # sso_built_url = auth.login()
    # request.session['AuthNRequestID'] = auth.get_last_request_id()
    # return redirect(sso_built_url)


@saml_bp.route('/saml/slo')
def slo():
    """
    single logout from user. Redirects to IDP
    """
    logger.info('Initiating logout for user ' + get_logged_in_user())
    auth, _ = do_auth()
    name_id = session_index = name_id_format = name_id_nq = name_id_spnq = None
    if 'samlNameId' in session:
        name_id = session['samlNameId']
    if 'samlSessionIndex' in session:
        session_index = session['samlSessionIndex']
    if 'samlNameIdFormat' in session:
        name_id_format = session['samlNameIdFormat']
    if 'samlNameIdNameQualifier' in session:
        name_id_nq = session['samlNameIdNameQualifier']
    if 'samlNameIdSPNameQualifier' in session:
        name_id_spnq = session['samlNameIdSPNameQualifier']

    return redirect(
        auth.logout(name_id=name_id, session_index=session_index, nq=name_id_nq, name_id_format=name_id_format,
                    spnq=name_id_spnq))


@saml_bp.route('/saml/sls')
def sls():
    """
    Process return from IDP after signing out.
    """
    auth, req = do_auth()
    request_id = _get_from_session('LogoutRequestID')
    timed_out = session.get('timed_out', None)
    url = auth.process_slo(request_id=request_id, delete_session_cb=lambda: session.clear())
    errors = auth.get_errors()
    if len(errors) == 0:
        if url is not None:
            # To avoid 'Open Redirect' attacks, before execute the redirection confirm
            # the value of the url is a trusted URL.
            return redirect(url)
        else:
            if timed_out:
                flash('Your session expired so you have been logged out. Please login again.', 'info')
            else:
                flash('Logged out', 'info')
            logger.info('Successful logout')
    elif auth.get_settings().is_debug_active():
        error_reason = auth.get_last_error_reason()
        flash('Failed to logout', 'error')
        logger.warning('Logout error occurred: ' + error_reason)

    return render_template('home.html')


@saml_bp.route('/saml/acs', methods=['POST'])
def acs():
    """
    Process return from IDP after we sign-in.
    """
    auth, req = do_auth()
    request_id = _get_from_session('AuthNRequestID')
    auth.process_response(request_id=request_id)
    errors = auth.get_errors()
    if not auth.is_authenticated():
        flash('User is not authenticated', 'error')
        logger.warning('User is not authenticated')

    if len(errors) == 0:
        store_in_session(auth)
        logger.info('Successful login for user ' + get_logged_in_user())
        _log_session_info(auth)
        load_permissions()
        name = get_name()
        welcome_name = name if name else get_logged_in_user()
        flash('Welcome <b>' + welcome_name + '</b>', 'info')
        self_url = OneLogin_Saml2_Utils.get_self_url(req)
        if 'RelayState' in request.form and self_url != request.form['RelayState']:
            # To avoid 'Open Redirect' attacks, before execute the redirection confirm
            # the value of the request.form['RelayState'] is a trusted URL.
            return redirect(auth.redirect_to(request.form['RelayState']))
    elif auth.get_settings().is_debug_active():
        error_reason = auth.get_last_error_reason()
        flash('Failed to login', 'error')
        logger.warning('Login error occurred: ' + error_reason)

    return redirect('/')


def _log_session_info(auth):
    expiry_secs = auth.get_session_expiration()
    if expiry_secs:
        expiry_formatted = datetime.utcfromtimestamp(expiry_secs).strftime('%Y-%m-%d %H:%M:%S')
        logger.info('SAML session valid until: ' + expiry_formatted)
    else:
        logger.info('SAML session unknown expiry time')


def init_saml_auth(req):
    auth = OneLogin_Saml2_Auth(req, custom_base_path=current_app.config['SAML_PATH'])
    return auth


def prepare_flask_request():
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'script_name': request.path,
        'get_data': request.args.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        'lowercase_urlencoding': True if current_app.config['ADFS'] == 'True' else False,
        'post_data': request.form.copy()
    }


def do_auth():
    req = prepare_flask_request()
    auth = init_saml_auth(req)
    return auth, req


def login_required(func):
    """
    Decorator to ensure login. Use this for each endpoint to be protected.
    e.g.
    .. code-block:: python

            @app.route("/")
            @login_required
            def index():
                return "Hello, World!"
    """
    @wraps(func)
    async def decorated_view(*args, **kwargs):
        if is_logged_in():
            return await func(*args, **kwargs)
        else:
            return redirect('/saml/sso')
    return decorated_view


def session_timeout():
    """
    If we are in a logged in state, then make sure we logout with the IDP.
    To be called when we are managing our own session timeout
    """
    if is_logged_in():
        logger.info("Session timed out so we must log out user")
        session['timed_out'] = True
        return redirect('/saml/slo')
    else:
        logger.info("Session timed out without login")
        session.clear()
        flash('Your session has expired - you may need to login again', 'info')
        return render_template('home.html')


def store_in_session(auth):
    """
    Store information in the session that we get during SAML login, particularly
    the identity name, the attributes, and some information which will be required
    when we logout.
    """
    if 'AuthNRequestID' in session:
        del session['AuthNRequestID']
    session['samlUserdata'] = auth.get_attributes()
    session['samlNameId'] = auth.get_nameid()
    session['samlNameIdFormat'] = auth.get_nameid_format()
    session['samlNameIdNameQualifier'] = auth.get_nameid_nq()
    session['samlNameIdSPNameQualifier'] = auth.get_nameid_spnq()
    session['samlSessionIndex'] = auth.get_session_index()


def _get_from_session(key):
    value = None
    if key in session:
        value = session[key]
    return value
