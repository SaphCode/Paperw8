from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)

bp = Blueprint('disclaimer', __name__)

@bp.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer/disclaimer.html')