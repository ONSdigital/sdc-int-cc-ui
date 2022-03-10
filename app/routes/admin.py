from flask import Blueprint, flash, render_template, request, redirect, url_for
from app.user_auth import login_required
from app.access import has_single_permission
from app.backend import CCSvc
from structlog import get_logger

admin_bp = Blueprint("admin", __name__)

logger = get_logger()


@admin_bp.route('/admin/')
@login_required
async def admin_home():
    return render_template('admin/home.html')


@admin_bp.route('/admin/user-list/')
@login_required
async def admin_user_list():
    users = await CCSvc().get_users()
    user_rows = _build_user_rows(users)
    return render_template('admin/user-list.html', user_rows=user_rows)


@admin_bp.route('/admin/update-user/<user_identity>/', methods=['GET', 'POST'])
@login_required
async def update_user(user_identity):
    if request.method == 'POST':
        logger.info("Updating user: " + user_identity)
        # call CCSvc to update user
        flash('User <b>' + user_identity + '</b> has been updated', 'info')
        return redirect(url_for('admin.admin_user_list'))
    else:
        page_title = 'Update user'
        return render_template('admin/update-user.html', page_title=page_title, user_identity=user_identity)


@admin_bp.route('/admin/delete-user/<user_identity>/', methods=['GET', 'POST'])
@login_required
async def delete_user(user_identity):
    if request.method == 'POST':
        logger.info("Deleting user: " + user_identity)
        await CCSvc().delete_user(user_identity)
        flash('User <b>' + user_identity + '</b> has been deleted', 'info')
        return redirect(url_for('admin.admin_user_list'))
    else:
        page_title = 'Remove user'
        return render_template('admin/delete-user.html', page_title=page_title, user_identity=user_identity)


def _build_actions(user_identity, user):
    actions = ''

    if has_single_permission('MODIFY_USER'):
        actions += '<a href="' + url_for('admin.update_user', user_identity=user_identity) + '">Change</a>'

    if has_single_permission('DELETE_USER') and user['deletable']:
        if actions:
            actions += ' | '
        actions += '<a href="' + url_for('admin.delete_user', user_identity=user_identity) + '">Delete</a>'

    return actions


def _build_name(user):
    surname = user['surname']
    if surname:
        name = user['forename'] + ' ' + surname
    else:
        name = '<i>(pending login)</i>'
    return name


def _build_user_rows(users):
    rows = []
    for user in users:
        identity = user['identity']
        status = 'success' if user['active'] else 'pending'
        status_text = 'Active' if user['active'] else 'Inactive'
        roles = ''
        for role in user['userRoles']:
            roles = roles + role + '<br/>'
        surveys = ''
        for survey in user['surveyUsages']:
            surveys = surveys + survey['surveyType'] + '<br/>'

        rows.append({
            'tds': [
                {
                    'value': '<b>' + identity + '</b>',
                    'tdClasses': 'ons-u-fs-r-b'
                },
                {
                    'value': _build_name(user)
                },
                {
                    'value': roles
                },
                {
                    'value': '<span class="ons-status ons-status--' + status + '">' + status_text + '</span>'
                },
                {
                    'value': surveys
                },
                {
                    'value': _build_actions(identity, user)
                }
            ]
        })
    return rows
