from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from flask_wtf import FlaskForm

from flask_pagedown.fields import PageDownField
from wtforms import StringField
from wtforms.validators import InputRequired, Length
from werkzeug.exceptions import abort

from datetime import datetime
import markdown 

from gbpartners.auth import login_required, admin_login_required
from gbpartners.db import get_db

bp = Blueprint('blog', __name__)

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    content = PageDownField('Markdown', validators=[InputRequired()])
    category = StringField('Category', validators=[InputRequired(), Length(max=50)])
    

@bp.route('/blog')
def blog():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, p.title, p.content, p.created, p.author_id, p.last_edit, p.category, u.display_name'
        ' FROM post p'
        ' JOIN user u ON p.author_id = u.id'
        ' ORDER BY last_edit DESC'
        ' LIMIT 5'
    ).fetchall()
    
    grouped_posts = db.execute(
        'SELECT id, title, category'
        ' FROM post p'
        ' GROUP BY category'
        ' ORDER BY category DESC'
    ).fetchall()

    return render_template('blog/blog.html', posts=posts, grouped_posts=grouped_posts)

@bp.route('/post/<title>')    
def post(title):
    db = get_db()
    post = db.execute(
        'SELECT p.id AS id, title, content, created, last_edit, display_name, u.id AS author_id, username'
        ' FROM post p'
        ' JOIN user u ON p.author_id = u.id'
        ' WHERE title = ?',
        (title,)
    ).fetchone()
    
    post = dict(post)
    post['content'] = markdown.markdown(post['content'])
    return render_template('blog/post.html', post=post)
    
    
@bp.route('/blog/create', methods=('GET', 'POST'))
@login_required
def create():
    form = BlogForm()
    if form.validate_on_submit():
        db = get_db()
        db.execute(
            'INSERT INTO post (author_id, title, content, category, last_edit)'
            ' VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)',
            (g.user['id'], form.title.data, form.content.data, form.category.data)
        )
        db.commit()
        return redirect(url_for('blog.blog'))
    return render_template('blog/create.html', form=form)


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, content, created, author_id, category'
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
    post = get_post(id)
    
    form = BlogForm(title=post['title'], content=post['content'], category=post['category'])

    if form.validate_on_submit():
        db = get_db()
        db.execute(
            'UPDATE post SET title = ?, content = ?, category = ?, last_edit = CURRENT_TIMESTAMP'
            ' WHERE id = ?',
            (form.title.data, form.content.data, form.category.data, id)
        )
        db.commit()
        return redirect(url_for('blog.blog'))

    return render_template('blog/update.html', form=form, post=post)
    
    
@bp.route('/blog/<int:id>/delete', methods=('POST',))
@admin_login_required
def delete(id):
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.blog'))