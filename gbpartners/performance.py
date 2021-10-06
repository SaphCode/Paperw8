from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from gbpartners.db import get_db

import json

bp = Blueprint('performance', __name__)


@bp.route('/')
def index():
    db = get_db()
    
    query = db.execute('SELECT CAST(strftime("%Y", MIN(date)) AS INTEGER) as min_year, CAST(strftime("%Y", MAX(date)) AS INTEGER) as max_year'
        ' FROM historical_performance'
    ).fetchone()
    
    years = [query['min_year'] + i for i in range(query['max_year']-query['min_year']+1)]
    
    return render_template('performance/portfolio.html', active='home', years=years)