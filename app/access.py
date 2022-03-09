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


def has_any_role():
    return 'permissions' in session and session['permissions']


def has_any_admin_role():
    return 'adminRoles' in session and session['adminRoles']


def can_admin_roles():
    return has_single_permission('USER_ROLE_MAINTENANCE') and has_any_admin_role()


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


def is_admin_of_role(role):
    if has_single_permission('RESERVED_USER_ROLE_ADMIN'):
        return True
    elif has_single_permission('USER_ROLE_MAINTENANCE'):
        return ('adminRoles' in session) and (role in session['adminRoles'])


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
                    has_permission=has_single_permission, permit_class=permit_class,
                    has_any_role=has_any_role, can_admin_roles=can_admin_roles)
