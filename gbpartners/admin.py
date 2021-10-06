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
from gbpartners.utils import process_performance_file

import os
import csv

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
        'SELECT id, username, display_name'
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
        'SELECT id, title, category, created, last_edit'
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


@bp.route('/admin/upload_performance', methods=['GET', 'POST'])
@admin_login_required
def upload_performance_file():
    form = UploadPerformanceForm()

    if form.validate_on_submit():
        # todo secure filename
        filename = secure_filename(form.file_field.data.filename)
        root_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'data')
        destination = os.path.join(root_dir, filename)
        form.file_field.data.save(destination)
        process_performance_file(root_dir, filename, get_db())
        
        
        db = get_db()
        
        historical_snp_performance = db.execute(
            'SELECT date, name, cum_return'
            ' FROM historical_performance'
            ' WHERE name = "SPXTR"'
        ).fetchall()
        performance = [(row['date'], row['name'].replace('\\n', ''), row['cum_return']) for row in historical_snp_performance]
        
        historical_portfolio_performance = db.execute(
            'SELECT date, name, cum_return'
            ' FROM historical_performance'
            ' WHERE name = "PORTFOLIO"'
        ).fetchall()
        performance.extend([(row['date'], row['name'].replace('\\n', ''), row['cum_return']) for row in historical_portfolio_performance])

        with open(os.path.join(root_dir, 'performance_measurement.csv'), 'w') as f:
            writer = csv.writer(f, lineterminator= '\n')
            writer.writerow(['date', 'name', 'cum_return'])
            writer.writerows(performance)

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
            form.file_field.data.save(os.path.join(directory, form.file_field.data.filename))
        else:
            flash('No directory supplied.')
        return redirect(url_for('admin.upload_image_file'))
        
    return render_template('admin/upload_image.html', form=form)
           
           