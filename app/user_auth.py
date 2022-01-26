
from flask import (request, render_template, redirect, session,
                   make_response, current_app, Blueprint, flash)

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from functools import wraps

saml_bp = Blueprint('saml', __name__)


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
    current_app.logger.info('Initiating login')
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
    current_app.logger.info('Initiating logout for user ' + get_logged_in_user())
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
    request_id = get_from_session('LogoutRequestID')
    url = auth.process_slo(request_id=request_id, delete_session_cb=lambda: session.clear())
    errors = auth.get_errors()
    if len(errors) == 0:
        if url is not None:
            # To avoid 'Open Redirect' attacks, before execute the redirection confirm
            # the value of the url is a trusted URL.
            return redirect(url)
        else:
            flash('Logged out', 'info')
            current_app.logger.info('Successful logout')
    elif auth.get_settings().is_debug_active():
        error_reason = auth.get_last_error_reason()
        flash('Failed to logout', 'error')
        current_app.logger.warning('Logout error occurred: ' + error_reason)

    return render_template('home.html')


@saml_bp.route('/saml/acs', methods=['POST'])
def acs():
    """
    Process return from IDP after we sign-in.
    """
    auth, req = do_auth()
    request_id = get_from_session('AuthNRequestID')
    auth.process_response(request_id=request_id)
    errors = auth.get_errors()
    if not auth.is_authenticated():
        flash('User is not authenticated', 'error')
        current_app.logger.warning('User is not authenticated')

    if len(errors) == 0:
        store_in_session(auth)
        current_app.logger.info('Successful login for user ' + get_logged_in_user())
        name = get_name()
        welcome_name = name if name else  get_logged_in_user()
        flash('Welcome <b>' + welcome_name + '</b>', 'info')
        self_url = OneLogin_Saml2_Utils.get_self_url(req)
        if 'RelayState' in request.form and self_url != request.form['RelayState']:
            # To avoid 'Open Redirect' attacks, before execute the redirection confirm
            # the value of the request.form['RelayState'] is a trusted URL.
            return redirect(auth.redirect_to(request.form['RelayState']))
    elif auth.get_settings().is_debug_active():
        error_reason = auth.get_last_error_reason()
        flash('Failed to login', 'error')
        current_app.logger.warning('Login error occurred: ' + error_reason)

    return render_template('home.html')


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
        if 'samlNameId' in session and len(session['samlNameId']) > 0:
            return await func(*args, **kwargs)
        else:
            return redirect('/saml/sso')
    return decorated_view


def store_in_session(auth):
    if 'AuthNRequestID' in session:
        del session['AuthNRequestID']
    session['samlUserdata'] = auth.get_attributes()
    session['samlNameId'] = auth.get_nameid()
    session['samlNameIdFormat'] = auth.get_nameid_format()
    session['samlNameIdNameQualifier'] = auth.get_nameid_nq()
    session['samlNameIdSPNameQualifier'] = auth.get_nameid_spnq()
    session['samlSessionIndex'] = auth.get_session_index()


def get_from_session(key):
    value = None
    if key in session:
        value = session[key]
    return value


def get_logged_in_user():
    return session.get('samlNameId', 'nobody')


def get_attributes():
    attributes = None
    if 'samlUserdata' in session:
        if len(session['samlUserdata']) > 0:
            attributes = session['samlUserdata']
            current_app.logger.info('attributes: ' + str(attributes))
    return attributes


def get_name():
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


def setup_auth_utilities(application):
    """
    Set up utility methods that can be called from the jinja2 HTML templates.
    """
    @application.context_processor
    def utility_processor():
        def get_id():
            return get_logged_in_user()

        def is_logged_in():
            return 'samlNameId' in session and len(session['samlNameId']) > 0

        return dict(get_id=get_id, is_logged_in=is_logged_in)
