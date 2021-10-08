from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)

bp = Blueprint('contact', __name__)

@bp.route('/contact')
def contact():
    return render_template('contact/contact.html')