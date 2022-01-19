from flask import Blueprint
from flask import render_template, request, redirect, url_for
from user_auth import login_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route('/admin/')
@login_required
async def admin_home():
    return render_template('admin/home.html')


@admin_bp.route('/admin/user-list/')
@login_required
async def admin_user_list():
    return render_template('admin/user-list.html')


@admin_bp.route('/admin/update-user/<username>/', methods=['GET', 'POST'])
@login_required
async def update_user(username):
    if request.method == 'POST':
        return redirect(url_for('admin.user_updated'))

    else:
        page_title = 'Update user'
        return render_template('admin/update-user.html', page_title=page_title, username=username)


@admin_bp.route('/admin/user-updated/', methods=['GET'])
@login_required
async def user_updated():
    return render_template('admin/user-updated.html')


@admin_bp.route('/admin/remove-user/<username>/', methods=['GET', 'POST'])
@login_required
async def remove_user(username):
    if request.method == 'POST':
        return redirect(url_for('admin.user_removed'))

    else:
        page_title = 'Remove user'
        return render_template('admin/remove-user.html', page_title=page_title, username=username)


@admin_bp.route('/admin/user-removed/', methods=['GET'])
@login_required
async def user_removed():
    return render_template('admin/user-removed.html')
