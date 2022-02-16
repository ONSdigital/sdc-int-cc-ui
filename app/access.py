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
        if is_logged_in() and 'permissions' not in session:
            logger.debug('Getting user permissions')
            perms = await CCSvc().get_permissions()
            session['permissions'] = perms
        return await func(*args, **kwargs)
    return ensure_permissions


def _has_any_permission(perms=set()):
    if 'permissions' in session:
        user_perms = set(session['permissions'])
        return bool(set(perms).intersection(user_perms))
    else:
        return False


def permit_class(perm, permitted_class):
    return permitted_class if has_single_permission(perm) else 'ons-u-hidden'


def has_single_permission(perm):
    perms = set()
    perms.add(perm)
    return _has_any_permission(perms)


def view_admin():
    return _has_any_permission({'CAN_MANAGE_SYSTEM'})


def view_sel():
    return _has_any_permission({'CAN_RECEIVE_INBOUND_CALLS'})


def view_tops():
    return _has_any_permission({'CAN_MAKE_OUTBOUND_CALLS'})


def setup_access_utilities(application):
    """
    Set up utility methods that can be called from the jinja2 HTML templates.
    """
    @application.context_processor
    def utility_processor():
        return dict(view_admin=view_admin, view_sel=view_sel, view_tops=view_tops,
                    has_permission=has_single_permission, permit_class=permit_class)
