import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from paperw8.database.db import get_db

import os

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/<username>/profile')
def profile(username):
    db = get_db()
    
    # get user with given username from db
    user = db.execute(
        "SELECT *"
        " FROM user"
        " WHERE username=?",
        (username,)
    ).fetchone()
    
    # load the images in that users directory
    images = os.listdir(os.path.join(current_app.static_folder, f'images/profile/{username}/side'))
    
    # render the html with the given user and the images found
    return render_template('user/user.html', user=user, images=images)