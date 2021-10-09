from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)

bp = Blueprint('janik', __name__)

@bp.route('/user')
def contact():
    return render_template('user/user.html')