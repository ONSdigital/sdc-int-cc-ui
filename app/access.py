from functools import wraps
from app.user_auth import is_logged_in
from app.backend import CCSvc
from flask import session
from structlog import get_logger

logger = get_logger()

"""
Control access to resources. i.e police authorisation.
"""


def load_permissions(func):
    """
    Decorator to load permissions
    """
    @wraps(func)
    async def ensure_permissions(*args, **kwargs):
        if is_logged_in():
            logger.debug('Getting user permissions')
            perms = await CCSvc().get_permissions()
            session['permissions'] = perms
        return await func(*args, **kwargs)
    return ensure_permissions


def _has_any_permission(perms=set()):
    if 'permissions' in session:
        user_perms = set(session['permissions'])
        return ('SUPER_USER' in user_perms) or bool(set(perms).intersection(user_perms))
    else:
        return False


def view_admin():
    return _has_any_permission()


def view_sel():
    return _has_any_permission()


def view_tops():
    return _has_any_permission()


def setup_access_utilities(application):
    """
    Set up utility methods that can be called from the jinja2 HTML templates.
    """
    @application.context_processor
    def utility_processor():
        return dict(view_admin=view_admin, view_sel=view_sel, view_tops=view_tops)
