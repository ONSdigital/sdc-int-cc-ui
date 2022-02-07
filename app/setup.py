from copy import deepcopy
from typing import Dict
from uuid import uuid4

import re

from flask import Flask
from flask import request as flask_request
from flask import session as cookie_session
from flask_talisman import Talisman
from flask_session import Session
from structlog import get_logger
from werkzeug import serving
from datetime import datetime

from app import settings
from app.jinja_filters import blueprint as filter_blueprint

from app.routes.admin import admin_bp
from app.routes.errors import errors_bp
from app.routes.case import case_bp
from app.routes.sel import sel_bp
from app.routes.structural import structural_bp
from app.routes.to import to_bp
from app.user_auth import saml_bp

from app.user_auth import setup_auth_utilities, session_timeout
from app.utilities.json import json_dumps

CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
}

CSP_POLICY = {
    "default-src": ["'self'"],
    "font-src": ["'self'"],
    "script-src": ["'self'", "'unsafe-inline'"],
    "style-src": ["'self'", "'unsafe-inline'"],
    "connect-src": ["'self'"],
    "frame-src": [],
    "img-src": ["'self'"],
    "object-src": ["'none'"],
    "base-uri": ["'none'"],
}

logger = get_logger()


def create_app(  # noqa: C901  pylint: disable=too-complex, too-many-statements
    setting_overrides=None,
):
    application = Flask(__name__, template_folder="../templates")
    application.config.from_object(settings)
    if setting_overrides:
        application.config.update(setting_overrides)
    application.cc = {}

    if application.config["APPLICATION_VERSION"]:
        logger.info(
            "starting cc",
            version=application.config["APPLICATION_VERSION"],
        )

    # IMPORTANT: This must be initialised *before* any other Flask plugins that add
    # before_request hooks. Otherwise any logging by the plugin in their before
    # request will use the logger context of the previous request.
    @application.before_request
    def before_request():  # pylint: disable=unused-variable
        request_id = str(uuid4())
        logger.new(request_id=request_id)

        url_path = flask_request.full_path

        if not url_path == '/info?':
            logger.info(
                "request",
                method=flask_request.method,
                url_path=url_path,
                session_cookie_present="session" in flask_request.cookies,
                csrf_token_present="csrf_token" in cookie_session,
                user_agent=flask_request.user_agent.string,
            )

    @application.before_request
    def check_for_session_timeout():
        now = datetime.now()
        last_active = cookie_session.get('last_active', None)
        cookie_session['last_active'] = now
        url_path = flask_request.full_path
        if last_active and url_path != '/saml/sso?':
            delta = now - last_active
            if delta.seconds > settings.SESSION_TIMEOUT_SECS:
                logger.info("session expired")
                return session_timeout()

    disable_endpoint_logs()

    setup_redis(application)

    setup_secure_headers(application)

    application.url_map.strict_slashes = False

    add_blueprints(application)

    add_info(application)

    setup_auth_utilities(application)

    setup_jinja_env(application)

    return application


def disable_endpoint_logs():
    """Disable logs for requests to healthcheck endpoints."""
    disabled_endpoints = ('/info', '/healthz')
    parent_log_request = serving.WSGIRequestHandler.log_request

    def log_request(self, *args, **kwargs):
        if not any(re.match(f"{de}$", self.path) for de in disabled_endpoints):
            parent_log_request(self, *args, **kwargs)

    serving.WSGIRequestHandler.log_request = log_request


def setup_jinja_env(application):
    # Enable whitespace removal
    application.jinja_env.trim_blocks = True
    application.jinja_env.lstrip_blocks = True

    # Switch off flask default autoescaping as schema content can contain html
    application.jinja_env.autoescape = False

    # pylint: disable=no-member
    application.jinja_env.add_extension("jinja2.ext.do")


def _add_cdn_url_to_csp_policy(cdn_url) -> Dict:
    csp_policy = deepcopy(CSP_POLICY)
    for directive in csp_policy:
        if directive not in ["frame-src", "object-src", "base-uri"]:
            csp_policy[directive].append(cdn_url)
    return csp_policy


def setup_secure_headers(application):
    csp_policy = _add_cdn_url_to_csp_policy(application.config["CDN_URL"])

    application.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    Talisman(
        application,
        content_security_policy=csp_policy,
        content_security_policy_nonce_in=["script-src"],
        session_cookie_secure=application.config["ENABLE_SECURE_SESSION_COOKIE"],
        force_https=False,  # this is handled at the firewall
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        frame_options="DENY",
    )


def setup_redis(application):
    Session(application)


def add_blueprints(application):

    application.register_blueprint(structural_bp)
    structural_bp.config = application.config.copy()

    application.register_blueprint(admin_bp)
    admin_bp.config = application.config.copy()

    application.register_blueprint(case_bp)
    case_bp.config = application.config.copy()

    application.register_blueprint(errors_bp)
    errors_bp.config = application.config.copy()

    application.register_blueprint(sel_bp)
    sel_bp.config = application.config.copy()

    application.register_blueprint(to_bp)
    to_bp.config = application.config.copy()

    application.register_blueprint(saml_bp)
    saml_bp.config = application.config.copy()

    application.register_blueprint(filter_blueprint)


def add_info(application):
    @application.route("/info")
    def info():  # pylint: disable=unused-variable
        data = {"env": application.config["FLASK_ENV"],
                "status": "OK", "version": application.config["APPLICATION_VERSION"]}
        return json_dumps(data)
