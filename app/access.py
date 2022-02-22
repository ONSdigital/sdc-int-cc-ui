from app.backend import CCSvc
from flask import session, flash
from structlog import get_logger

logger = get_logger()

"""
Control access to resources. i.e police authorisation.
"""


def load_permissions():
    """
    load permissions
    """
    logger.debug('Getting user permissions')
    perms = CCSvc().get_permissions()
    if not perms:
        flash('Your login user is not correctly setup or is inactive. ' +
              'Please ask an administrator to correctly configure roles, surveys and status for you.',
              'error')
    session['permissions'] = perms


def _has_any_permission(perms=None):
    if perms is None:
        return False
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
    return _has_any_permission({'CAN_MANAGE_SYSTEM', 'CAN_MANAGE_USERS'})


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
