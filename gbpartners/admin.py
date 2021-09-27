from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask_wtf import FlaskForm
from wtforms import FileField, StringField
from wtforms.validators import regexp, DataRequired, Length

from gbpartners.auth import admin_login_required
from gbpartners.db import get_db

import os
import pandas as pd

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
    if len(users) > 0:
        columns = users[0].keys()
        return render_template('admin/database/database.html', columns = columns, rows = users, table_name = 'user')
    return render_template('admin/database/database.html')


@bp.route('/admin/post')
@admin_login_required
def post_list():
    db = get_db()
    posts = db.execute(
        'SELECT id, title'
        ' FROM post'
    ).fetchall()
    if len(posts) > 0:
        columns = posts[0].keys()
        return render_template('admin/database/database.html', columns = columns, rows = posts, table_name = 'post')
    return render_template('admin/database/database.html')


class UploadPerformanceForm(FlaskForm):
    performance_file = FileField('Performance', validators=[DataRequired(), regexp('^.*\.csv', message="File must end in: .csv")])
    
    
class UploadImageForm(FlaskForm):
    destination = StringField('Folder', validators=[DataRequired(), Length(min=1)])
    image_file = FileField('Image', validators=[DataRequired(), regexp('^.*\.(jpg|JPG|jpeg|gif|png)', message="File must end in one of the following: .jpg, .JPG, .jpeg, .gif, .png")])


def processPerformanceFile(file):
    csv = pd.read_csv(file)
    print(csv)
    raise NotImplementedError()


@bp.route('/admin/upload_performance', methods=('GET', 'POST'))
@admin_login_required
def upload_performance_file():
    form = UploadPerformanceForm()
    
    if form.validate_on_submit():
        print('success')
        processPerformanceFile(form.performance_file.read())
        return redirect(url_for('admin.home'))
        
    return render_template('admin/upload_performance.html', form=form)


@bp.route('/admin/upload_image', methods=('GET', 'POST'))
@admin_login_required
def upload_image_file():
    form = UploadImageForm()

    if form.validate_on_submit():
        if not os.path.isdir(form.destination.data):
            os.mkdir(form.destination.data)
        with open(os.path.join(form.destination.data, form.image.data), 'w') as f:
            f.write(form.image.read())
           
        
    return render_template('admin/upload_image.html', form=form)
           
           