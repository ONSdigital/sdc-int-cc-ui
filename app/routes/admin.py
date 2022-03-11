from flask import Blueprint, flash, render_template, request, redirect, url_for
from app.user_auth import login_required
from app.user_context import get_logged_in_user
from app.access import has_single_permission, is_admin_of_role, can_admin_roles
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
    user = await CCSvc().get_user(user_identity)
    if request.method == 'POST':
        logger.info("Updating user: " + user_identity)
        roles = await CCSvc().get_roles()
        modified = await _update_active(user)
        modified = await _update_surveys(user) or modified
        modified = await _update_user_roles(user, roles) or modified
        modified = await _update_admin_roles(user, roles) or modified
        if modified:
            flash('User <b>' + user_identity + '</b> has been updated', 'info')
        else:
            flash('User <b>' + user_identity + '</b> has not been changed', 'info')
        return redirect(url_for('admin.admin_user_list'))
    else:
        return await _render_update_user(user_identity, user)


async def _update_active(user):
    if has_single_permission('MODIFY_USER'):
        active_checked = 'active' in request.form
        if user['active'] != active_checked:
            await CCSvc().modify_user(user['identity'], active_checked)
            return True
    return False


async def _update_surveys(user):
    if has_single_permission('USER_SURVEY_MAINTENANCE'):
        checked_surveys = _checked_boxes('surveys')
        existing_surveys = [i['surveyType'] for i in user['surveyUsages']]
        if existing_surveys != checked_surveys:
            survey_types = await CCSvc().get_survey_types()
            for survey_type in survey_types:
                if (survey_type in checked_surveys) and (survey_type not in existing_surveys):
                    await CCSvc().add_user_survey(user['identity'], survey_type)
                elif (survey_type not in checked_surveys) and (survey_type in existing_surveys):
                    await CCSvc().remove_user_survey(user['identity'], survey_type)
            return True
    return False


async def _update_user_roles(user, roles):
    if has_single_permission('RESERVED_USER_ROLE_ADMIN') or can_admin_roles():
        checked_user_roles = _checked_boxes('user_roles')
        existing_roles = user['userRoles']
        if existing_roles != checked_user_roles:
            for role_obj in roles:
                role = role_obj['name']
                if not is_admin_of_role(role):
                    continue
                if (role in checked_user_roles) and (role not in existing_roles):
                    await CCSvc().add_user_role(user['identity'], role)
                elif (role not in checked_user_roles) and (role in existing_roles):
                    await CCSvc().remove_user_role(user['identity'], role)
            return True
    return False


async def _update_admin_roles(user, roles):
    if has_single_permission('RESERVED_ADMIN_ROLE_MAINTENANCE'):
        checked_user_roles = _checked_boxes('admin_roles')
        existing_roles = user['adminRoles']
        if existing_roles != checked_user_roles:
            for role_obj in roles:
                role = role_obj['name']
                if (role in checked_user_roles) and (role not in existing_roles):
                    await CCSvc().add_admin_role(user['identity'], role)
                elif (role not in checked_user_roles) and (role in existing_roles):
                    await CCSvc().remove_admin_role(user['identity'], role)
            return True
    return False


@admin_bp.route('/admin/add-user/', methods=['GET', 'POST'])
@login_required
async def add_user():
    if request.method == 'POST':
        user_identity = request.form['user-email']
        email_error_msg = ''
        if user_identity:
            logger.info("Creating user: " + user_identity)
            try:
                await CCSvc().add_user(user_identity)
                flash('User <b>' + user_identity + '</b> has been created', 'info')
                await _populate_created_user(user_identity)
            except UserExistsAlready:
                email_error_msg = 'The user exists already'
        else:
            email_error_msg = 'Please enter an email'

        if email_error_msg:
            flash(email_error_msg, 'error_email')
            return await _render_add_user(user_identity, email_error_msg)
        else:
            return redirect(url_for('admin.admin_user_list'))
    else:
        return await _render_add_user()


async def _render_user_input_page(operation, path, user_identity, user=None, active=True, email_error_msg=''):
    survey_types_checkboxes = await _build_survey_types(user)
    roles = await CCSvc().get_roles()
    user_roles_checkboxes = _build_user_role_checkboxes(roles, user)
    admin_roles_checkboxes = _build_admin_role_checkboxes(roles, user)

    return render_template(path,
                           page_title=(operation + ' user'),
                           operation=operation,
                           survey_types_checkboxes=survey_types_checkboxes,
                           user_roles_checkboxes=user_roles_checkboxes,
                           admin_roles_checkboxes=admin_roles_checkboxes,
                           value_email=user_identity,
                           is_active=active,
                           error_email=email_error_msg)


async def _render_add_user(user_identity='', email_error_msg=''):
    return await _render_user_input_page('Add', 'admin/add-or-update-user.html', user_identity,
                                         user=None, active=True, email_error_msg=email_error_msg)


async def _render_update_user(user_identity, user):
    active = user['active'] if user else 'active' in request.form
    return await _render_user_input_page('Update', 'admin/add-or-update-user.html', user_identity, user, active)


def _checked_boxes(checkbox_name):
    return request.form.getlist(checkbox_name) if checkbox_name in request.form else []


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
    if user_identity != get_logged_in_user():
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
        user['userRoles'].sort()
        for role in user['userRoles']:
            roles = roles + role + '<br/>'
        surveys = ''
        user['surveyUsages'].sort()
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


async def _build_survey_types(user):
    if user:
        checked_surveys = [i['surveyType'] for i in user['surveyUsages']]
    else:
        checked_surveys = _checked_boxes('surveys')
    rows = []
    survey_types = await CCSvc().get_survey_types()
    for survey_type in survey_types:
        rows.append({
                "id": survey_type,
                "name": 'surveys',
                "label": {
                    "text": survey_type
                },
                "checked": survey_type in checked_surveys,
                "value": survey_type
        })
    return rows


def _build_user_role_checkboxes(roles, user):
    if user:
        checked_user_roles = user['userRoles']
    else:
        checked_user_roles = _checked_boxes('user_roles')
    return _build_role_checkboxes('user_roles', roles, checked_user_roles, True)


def _build_admin_role_checkboxes(roles, user):
    if user:
        checked_admin_roles = user['adminRoles']
    else:
        checked_admin_roles = _checked_boxes('admin_roles')
    admin_roles_checkboxes = []
    if has_single_permission('RESERVED_ADMIN_ROLE_MAINTENANCE'):
        admin_roles_checkboxes = _build_role_checkboxes('admin_roles', roles, checked_admin_roles)
    return admin_roles_checkboxes


def _build_role_checkboxes(checkbox_name, all_roles, checked_roles, check_auth=False):
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
                "checked": name in checked_roles,
                "value": name
        })
    return rows
