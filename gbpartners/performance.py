from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from gbpartners.db import get_db

bp = Blueprint('performance', __name__)

@bp.route('/')
def index():
    db = get_db()
    '''
    table = db.execute(
        'SELECT name'
        ' FROM sqlite_master'
        ' WHERE type="table" AND name="historical_performance"'
    ).fetchone()
    '''
    #if table is not None:
    historical_spy_performance = db.execute(
        'SELECT date, name, cum_return'
        ' FROM historical_performance'
        ' WHERE name = "SPXTR"'
    ).fetchall()
    historical_portfolio_performance = db.execute(
        'SELECT date, name, cum_return'
        ' FROM historical_performance'
        ' WHERE name = "PORTFOLIO"'
    ).fetchall()
    
    return render_template('performance/portfolio.html', active='home')