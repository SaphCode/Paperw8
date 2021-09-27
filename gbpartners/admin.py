from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from gbpartners.auth import admin_login_required
from gbpartners.db import get_db

bp = Blueprint('admin', __name__)

@bp.route('/admin/home')
@admin_login_required
def home():
    return render_template('admin/admin.html')

@bp.route('/admin/user')
@admin_login_required
def user_list():
    db = get_db()
    users = db.execute(
        'SELECT *'
        ' FROM user'
    ).fetchall()
    print(users)
    if len(users) > 0:
        columns = users[0].keys()
        return render_template('admin/database/database.html', columns = columns, rows = users, table_name = 'user')
    return render_template('admin/database/database.html')


@bp.route('/admin/post')
@admin_login_required
def post_list():
    db = get_db()
    print("HI")
    posts = db.execute(
        'SELECT id, title'
        ' FROM post'
    ).fetchall()
    print(posts)
    for post in posts:
        print(post['title'])
    if len(posts) > 0:
        columns = posts[0].keys()
        return render_template('admin/database/database.html', columns = columns, rows = posts, table_name = 'post')
    return render_template('admin/database/database.html')

    