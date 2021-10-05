import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from gbpartners.db import get_db

import os

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
    
    
    images = os.listdir(os.path.join(current_app.static_folder, f'images/profile/{username}/side'))
    images = [f'images/profile/{username}/side/' + image for image in images]
    
    
    return render_template('user/user.html', user=user, images=images)