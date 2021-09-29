import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from gbpartners.db import get_db

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/<username>/profile')
def profile(username):
    db = get_db()
    
    user = db.execute(
        "SELECT *"
        " FROM user"
        " WHERE username=?",
        (username,)
    ).fetchone()

    return render_template('user/user.html', user=user)