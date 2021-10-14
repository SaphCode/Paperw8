from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_from_directory
)
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

from flask_pagedown.fields import PageDownField
from wtforms import StringField, SelectField, SelectMultipleField
from wtforms.validators import InputRequired, Length
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename, safe_join

from datetime import datetime
import markdown 

from gbpartners.user.auth import login_required, admin_login_required
from gbpartners.database.db import get_db
from gbpartners.data_processing.utils import upload_file

from sqlite3 import OperationalError
import os



bp = Blueprint('blog', __name__)

class BlogForm(FlaskForm):
    ticker = StringField('Ticker')
    title = StringField('Title', validators=[InputRequired()])
    parent_dir = SelectField('Parent Directory', validators=[InputRequired()])
    html_file = FileField('Html', validators=[FileRequired(), FileAllowed(['html'], message='Only html allowed.')])
    pdf_file = FileField('PDF', validators=[FileRequired(), FileAllowed(['pdf'], message='Only pdf allowed.')])
    title_img = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'JPG', 'jpeg', 'gif'], message="File must end in one of the following: .jpg, .JPG, .jpeg, .gif, .png")])
    category = SelectField('Category', choices=[('business', 'Business'), ('annual', 'Annual Report'), ('education', 'Education')], validators=[InputRequired()])
    related_to = SelectMultipleField('Related to', coerce=int)
    
class UpdateForm(FlaskForm):  
    ticker = StringField('Ticker')
    title = StringField('Title', validators=[InputRequired()])
    html_file = FileField('Html', validators=[FileAllowed(['html'], message='Only html allowed.')])
    pdf_file = FileField('PDF', validators=[FileAllowed(['pdf'], message='Only pdf allowed.')])
    category = SelectField('Category', choices=[('business', 'Business'), ('annual', 'Annual Report'), ('education', 'Education')], validators=[InputRequired()])
    related_to = SelectMultipleField('Related to', coerce=int)
    
@bp.route('/blog')
def blog_redirect():
    return redirect(url_for('blog.blog', group_by='all', sort_by='date_desc', page=1))

@bp.route('/blog/<group_by>/<int:page>/<sort_by>')
def blog(group_by, sort_by, page):
    db = get_db()
    
    # sort sql string
    sql_sort = None
    if sort_by == 'date_desc':
        sql_sort = 'last_edit DESC'
    elif sort_by == 'date_asc':
        sql_sort = 'last_edit ASC'
    elif sort_by == 'title_desc':
        sql_sort = 'title DESC, last_edit DESC'
    elif sort_by == 'title_asc':
        sql_sort = 'title ASC, last_edit DESC'
   
    # build sql one by one
    sql = 'SELECT p.id, ticker, title, title_img_parent_dir, title_img, p.created, html_file, pdf_file, p.author_id, p.last_edit, p.category, u.display_name'\
            ' FROM post p'\
            ' JOIN user u ON p.author_id = u.id'
    # also build max posts sql
    sql_max_posts = 'SELECT COUNT(p.id) as number'\
            ' FROM post p'
    # build group by sql
    if group_by != 'all':
        statement = f' WHERE category="{group_by}"'
        sql += statement
        sql_max_posts += statement
    # order
    sql += f' ORDER BY {sql_sort}'
    # limit
    sql += f' LIMIT {5*page}'
    
    # get max number of posts
    max_posts = db.execute(sql_max_posts).fetchone()['number']
    
    # get posts
    posts = []
    try:
        posts = db.execute(sql).fetchall()
    except OperationalError as e:
        flash(e)
    
    return render_template('blog/blog.html', active='blog', posts=posts, page=page, sort_by=sort_by, group_by=group_by, max_posts=max_posts)


@bp.route('/post/<title>/download/<path:filename>')
def download_post(title, filename):
    db = get_db()
    post = db.execute(
        'SELECT title_img_parent_dir AS parent_dir, pdf_file'
        ' FROM post'
        f' WHERE title="{title}"'
    ).fetchone()
    
    root_dir = current_app.config['UPLOAD_FOLDER']
    data_dir = 'data'
    parent_dir = post['parent_dir']
    
    print(os.getcwd())
    print(os.path.join(root_dir, data_dir, parent_dir, post["pdf_file"]))

    return send_from_directory(os.path.join(current_app.config['UPLOAD_FOLDER'], data_dir, parent_dir), path=os.path.join(root_dir, data_dir, parent_dir, post["pdf_file"]), as_attachment=True)


@bp.route('/post/<title>')    
def post(title):
    # get db
    db = get_db()
    
    # get post by title
    post = db.execute(
        'SELECT p.id AS id, ticker, author_id, title, category, title_img_parent_dir, title_img, html_file, pdf_file, created, last_edit, display_name, username'
        ' FROM post p'
        ' JOIN user u ON p.author_id = u.id'
        ' WHERE title = ?',
        (title,)
    ).fetchone()
    
    # get related posts by joining on both columns of the related table (see schema.sql)
    # left -> right
    related_posts_id = db.execute(
        'SELECT DISTINCT r.related_to_id AS related_id' # , title, title_img_parent_dir, title_img, created, display_name, username
        ' FROM post p'
        ' JOIN related r ON r.id = p.id'
        f' WHERE r.id = {post["id"]}'
    ).fetchall()
    
    # left <- right
    related_posts_id_2 = db.execute(
        'SELECT DISTINCT r.id AS related_id'
        ' FROM post p'
        ' JOIN related r ON r.related_to_id = p.id'
        f' WHERE p.id = {post["id"]}'
    ).fetchall()
    
    # left <-> right
    related_posts_id.extend(related_posts_id_2)
    related_posts_id = [related_post['related_id'] for related_post in related_posts_id]
    
    # find the ids in the post table and get the relevant columns
    related_posts = []
    for id in related_posts_id:
        related_posts.append(db.execute(
            'SELECT p.id, title, html_file, title_img_parent_dir, title_img, created, display_name, username'
            ' FROM post p'
            ' JOIN user u ON u.id=p.author_id'
            f' WHERE p.id={id}'
        ).fetchone())
    
    # don't include the post that's being viewed in related
    filtered_related_posts = []
    for related_post in related_posts:
        if related_post['title'] == post['title']:
            continue
        filtered_related_posts.append(related_post)
        
    post = dict(post)
    
    print(os.path.join(current_app.config['UPLOAD_FOLDER'], 'data', post['title_img_parent_dir'], post['html_file']))
    
    '''
    import codecs
    html_content = codecs.open(os.path.join('gbpartners', 'static', 'data', post['title_img_parent_dir'], post['html_file']), 'r').read()
    print(html_content)
    '''

    return render_template('blog/post.html', html_file=os.path.join(current_app.config['UPLOAD_FOLDER'], 'data', post['title_img_parent_dir'], post['html_file']), post=post, related_posts=filtered_related_posts)
    
    
@bp.route('/blog/create', methods=('GET', 'POST'))
@login_required
def create():
    # create a blog wtform
    form = BlogForm()
    
    # get db connection
    db = get_db()
    query = db.execute('SELECT id, title FROM post').fetchall()
    
    # load all dirs into Parent dir field
    root_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
    
    choices_parent = [(name.lower(), name) for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name))]
    form.parent_dir.choices = choices_parent
    
    # load all titles into the MultipleSelectField
    choices_posts = [(row['id'], row['title']) for row in query]
    form.related_to.choices = choices_posts
    
    # validate form
    if form.validate_on_submit():
    
        # get upload dir for html & pdf
        data_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'data')
        # get parent directory from form
        parent_dir = secure_filename(form.parent_dir.data)
        # get secure filename
        html_filename = secure_filename(form.html_file.data.filename)
        pdf_filename = secure_filename(form.pdf_file.data.filename)
        
        html_path = os.path.join(root_dir, parent_dir, html_filename)
        pdf_path = os.path.join(root_dir, parent_dir, pdf_filename)
            
        try:
            upload_file(os.path.join(data_dir, parent_dir), html_filename, form.html_file.data)
            upload_file(os.path.join(data_dir, parent_dir), pdf_filename, form.pdf_file.data)
        except FileExistsError as e:
            return render_template('blog/create.html', form=form, error=e)
    
        # get upload dir
        image_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
        # get secure filename
        filename = secure_filename(form.title_img.data.filename)
        
        # upload image (dir, filename, file (form.field.data))
        try:
            upload_file(os.path.join(image_dir, parent_dir), filename, form.title_img.data)
        except FileExistsError as e:
            return render_template('blog/create.html', form=form, error=e)
        
        # save the path in db so we can load it from html later
        title_img_parent = parent_dir
        title_img_path = filename
    
        # insert new post
        db.execute(
            'INSERT INTO post (author_id, title, ticker, html_file, pdf_file, title_img_parent_dir, title_img, category, last_edit)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)',
            (g.user['id'], form.title.data, form.ticker.data, html_filename, pdf_filename, title_img_parent, title_img_path, form.category.data)
        )
        # get last inserted id
        query = db.execute(
            'SELECT last_insert_rowid() as last_id'
        ).fetchone()

        last_id = query['last_id']
        # get selected related post ids
        id_list = form.related_to.data

        # for every related post, insert a record into related table
        for related_id in id_list:
            db.execute(
                'INSERT INTO related (id, related_to_id)'
                ' VALUES (?, ?)',
                (last_id, related_id)
            )
        # commit the transaction
        db.commit()
        return redirect(url_for('blog.blog', group_by='all', sort_by='date_desc', page=1))
    return render_template('blog/create.html', form=form)


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, ticker, content, created, author_id, category'
        ' FROM post p'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if (g.user['username'] != 'admin'):
        if (check_author and post['author_id'] != g.user['id']):
            abort(403)

    return post
    
    
@bp.route('/blog/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    # get the post that should be updated
    post = get_post(id)
    
    # create form
    form = UpdateForm(ticker=post['ticker'], title=post['title'], category=post['category'])
    
    # get db connection
    db = get_db()
    query = db.execute('SELECT id, title FROM post').fetchall()
    
    # load all titles into the MultipleSelectField
    choices_posts = [(row['id'], row['title']) for row in query]
    form.related_to.choices = choices_posts

    if form.validate_on_submit():
    
    
        # get upload dir
        data_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'data')
        # get parent directory from form
        parent_dir = secure_filename(post['title_img_parent_dir'])
        
        if form.html_file.data.filename:
            # get secure filename
            html_filename = secure_filename(form.html_file.data.filename)
            html_path = os.path.join(root_dir, parent_dir, html_filename)
            if os.path.isfile(html_path):
                os.remove(html_path)
            try:
                upload_file(os.path.join(data_dir, parent_dir), html_filename, form.html_file.data)
            except Error as e:
                return render_template('blog/create.html', form=form, error=e)
            
        if form.pdf_file.data.filename:
            pdf_filename = secure_filename(form.pdf_file.data.filename)
            pdf_path = os.path.join(root_dir, parent_dir, pdf_filename)
            if os.path.isfile(pdf_path):
                os.remove(pdf_path)
            try:
                upload_file(os.path.join(data_dir, parent_dir), pdf_filename, form.pdf_file.data)
            except Error as e:
                return render_template('blog/create.html', form=form, error=e)        
    
        # get db connection
        db = get_db()
        # update post
        db.execute(
            'UPDATE post SET title = ?, ticker = ?, html_file = ?, pdf_file = ?, category = ?, last_edit = CURRENT_TIMESTAMP'
            ' WHERE id = ?',
            (form.title.data, form.ticker.data, html_filename, pdf_filename, form.category.data, id)
        )
        db.commit()
        return redirect(url_for('blog.blog', group_by='all', sort_by='date_desc', page=1))

    return render_template('blog/update.html', form=form, post=post)
    
    
@bp.route('/blog/<int:id>/delete', methods=('POST',))
@admin_login_required
def delete(id):
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.blog', group_by='all', sort_by='date_desc', page=1))