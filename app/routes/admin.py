from flask import Blueprint, flash, render_template, request, redirect, url_for
from app.user_auth import login_required
from app.access import has_single_permission, is_admin_of_role
from app.backend import CCSvc
from structlog import get_logger
from app.routes.errors import UserExistsAlready

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


@admin_bp.route('/admin/create-user/', methods=['GET', 'POST'])
@login_required
async def create_user():
    survey_types = await _build_survey_types()
    roles = await CCSvc().get_roles()
    user_roles = _build_roles('user_roles', roles, True)
    admin_roles = _build_roles('admin_roles', roles) if has_single_permission('RESERVED_ADMIN_ROLE_MAINTENANCE') else []

    if request.method == 'POST':
        user_identity = request.form['user-email']
        email_error_msg = ''
        if user_identity:
            logger.info("Creating user: " + user_identity)
            try:
                await CCSvc().create_user(user_identity)
                flash('User <b>' + user_identity + '</b> has been created', 'info')
                await _populate_created_user(user_identity)
            except UserExistsAlready:
                email_error_msg = 'User exists already'
        else:
            email_error_msg = 'Enter an email'

        if email_error_msg:
            flash(email_error_msg, 'error_email')
            return render_template('admin/create-user.html', page_title='Create user',
                                   survey_types=survey_types, user_roles=user_roles, admin_roles=admin_roles,
                                   error_email=email_error_msg)
        else:
            return redirect(url_for('admin.admin_user_list'))
    else:
        return render_template('admin/create-user.html', page_title='Create user',
                               survey_types=survey_types, user_roles=user_roles, admin_roles=admin_roles)


async def _populate_created_user(user_identity):
    if 'surveys' in request.form:
        for survey_type in request.form.getlist('surveys'):
            logger.info('adding survey:' + survey_type + ' for user: ' + user_identity)
            await CCSvc().add_user_survey(user_identity, survey_type)
    else:
        logger.info('no surveys')
    if 'user_roles' in request.form:
        for role in request.form.getlist('user_roles'):
            logger.info('adding user role:' + role + ' for user: ' + user_identity)
            await CCSvc().add_user_role(user_identity, role)
    else:
        logger.info('no user roles')
    if 'admin_roles' in request.form:
        for role in request.form.getlist('admin_roles'):
            logger.info('adding admin role:' + role + ' for user: ' + user_identity)
            await CCSvc().add_admin_role(user_identity, role)
    else:
        logger.info('no admin roles')


@admin_bp.route('/admin/delete-user/<user_identity>/', methods=['GET', 'POST'])
@login_required
async def delete_user(user_identity):
    if request.method == 'POST':
        logger.info("Deleting user: " + user_identity)
        await CCSvc().delete_user(user_identity)
        flash('User <b>' + user_identity + '</b> has been deleted', 'info')
        return redirect(url_for('admin.admin_user_list'))
    else:
        return render_template('admin/delete-user.html', page_title='Delete user', user_identity=user_identity)


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


async def _build_survey_types():
    rows = []
    survey_types = await CCSvc().get_survey_types()
    for survey_type in survey_types:
        rows.append({
                "id": survey_type,
                "name": 'surveys',
                "label": {
                    "text": survey_type
                },
                "value": survey_type
        })
    return rows


def _build_roles(checkbox_name, all_roles, check_auth=False):
    rows = []
    for role in all_roles:
        name = role['name']
        if check_auth and (not is_admin_of_role(name)):
            continue
        rows.append({
                "id": name,
                "name": checkbox_name,
                "label": {
                    "text": name
                },
                "value": name
        })
    return rows
