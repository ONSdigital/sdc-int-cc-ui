from . import admin_bp
from flask import render_template


@admin_bp.route('/admin/')
async def admin_home():
    return render_template('admin/home.html')


@admin_bp.route('/admin/user-list/')
async def admin_user_list():
    return render_template('admin/user-list.html')
