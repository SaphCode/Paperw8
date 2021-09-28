from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired, Length
from werkzeug.utils import secure_filename

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
        'SELECT id, title, created, last_edit'
        ' FROM post'
    ).fetchall()
    if len(posts) > 0:
        columns = posts[0].keys()
        return render_template('admin/database/database.html', columns = columns, rows = posts, table_name = 'post')
    return render_template('admin/database/database.html')


class UploadPerformanceForm(FlaskForm):
    file_field = FileField() #, validators=[FileRequired(), FileAllowed(['csv'], message='File allowed: .csv')]
    
    
class UploadImageForm(FlaskForm):
    destination = SelectField('Folder')
    new_folder = StringField('New Folder')
    file_field = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'JPG', 'jpeg', 'gif'], message="File must end in one of the following: .jpg, .JPG, .jpeg, .gif, .png")])


def process_performance_file(file):
    csv = pd.read_csv(file)
    print(csv)
    raise NotImplementedError()


@bp.route('/admin/upload_performance', methods=['GET', 'POST'])
@admin_login_required
def upload_performance_file():
    form = UploadPerformanceForm()

    if form.validate_on_submit():
        # todo secure filename
        filename = secure_filename(form.photo.data.filename)
        form.file_field.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('admin.upload_performance_file'))

    return render_template('admin/upload_performance.html', form=form)


@bp.route('/admin/upload_image', methods=('GET', 'POST'))
@admin_login_required
def upload_image_file():
    form = UploadImageForm()
    
    root_dir = current_app.config['UPLOAD_FOLDER']
    choices = [(name.lower(), name) for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name))]
    choices.append(('', ''))
    form.destination.choices = choices
    
    if form.validate_on_submit():
        directory = None
        if form.new_folder.data:
            if not os.path.isdir(os.path.join(root_dir, form.new_folder.data)):
                directory = os.path.join(root_dir, form.new_folder.data)
                os.mkdir(directory)
        
        if form.destination.data:
            directory = os.path.join(root_dir, form.destination.data)
        
        if directory:
            print(directory)
            print(form.file_field.data.filename)
            print(os.path.join(directory, form.file_field.data.filename))
            form.file_field.data.save(os.path.join(directory, form.file_field.data.filename))
        else:
            flash('No directory supplied.')
        return redirect(url_for('admin.upload_image_file'))
        
    return render_template('admin/upload_image.html', form=form)
           
           