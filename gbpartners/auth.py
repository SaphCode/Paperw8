import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length
from werkzeug.security import check_password_hash, generate_password_hash

from gbpartners.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

class RegisterForm(FlaskForm):
    display_name = StringField(validators=[DataRequired()])
    username = StringField(validators=[DataRequired(), Length(min=1, max=20)])
    password = PasswordField(validators=[DataRequired(), Length(min=8, max=100)])

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
    
def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        username_logged_in = session.get('username', None)
        if g.user is None or username_logged_in is None or username_logged_in!='admin':
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    
    return wrapped_view

@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            db.commit()
        except db.IntegrityError:
                error = f"User {username} is already registered."
        else:
            return redirect(url_for("auth.login"))
    return render_template('auth/register.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            g.user = db.execute(
                'SELECT * FROM user WHERE id = ?', (user['id'],)
            ).fetchone()
            if user['username'] == 'admin':
                return redirect(url_for('admin.home'))
            return redirect(url_for('blog.blog'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    g.user = None
    return redirect(url_for('performance.index'))
    
    
@bp.route('/user/<username>/edit', methods=('GET', 'POST'))
def edit(username):
    if request.method == 'POST':
        username = request.form['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        error = None
        
        db = get_db()
        # get the user
        user = db.execute(
            "SELECT username, password"
            " FROM user"
            f" WHERE username=\'{username}\'"
        ).fetchone()

        if not user:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], old_password):
            error = 'Incorrect password.'
            
        if error is None:
            db.execute(
                "UPDATE user"
                f" SET password=\'{generate_password_hash(new_password)}\'"
                f" WHERE username=\'{username}\'"
            )
            db.commit()
            return redirect('/')
        
        flash(error)
    
    if username is not None:
        return render_template('auth/edit.html', username = username)
    return render_template('auth/edit.html')
    
    
@bp.route('/user/<int:id>/delete', methods=['POST'])
@admin_login_required
def delete(id):
    db = get_db()
    
    db.execute(
        "DELETE from user"
        f" WHERE id={id}"
    ).fetchone()
    
    db.commit()
    return redirect(url_for('blog.blog'))