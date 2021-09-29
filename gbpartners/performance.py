from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from gbpartners.db import get_db

import json

bp = Blueprint('performance', __name__)


@bp.route('/')
def index():
    #print(url_for('static', filename='portfolio.json'))
    #data = json.load(open(url_for('static', filename='portfolio.json')))
    return render_template('performance/portfolio.html', active='home')