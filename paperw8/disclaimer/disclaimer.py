from flask import (
    Blueprint, render_template
)

bp = Blueprint('disclaimer', __name__)

@bp.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer/disclaimer.html')