from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from gbpartners.db import get_db

import json

bp = Blueprint('performance', __name__)


@bp.route('/')
def index():
    return render_template('performance/portfolio.html', active='home')