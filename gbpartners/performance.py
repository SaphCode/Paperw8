from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from gbpartners.db import get_db

bp = Blueprint('performance', __name__)

@bp.route('/')
def index():
    db = get_db()
    historical_spy_performance = db.execute(
        'SELECT date, symbol, cum_return'
        ' FROM historical_performance'
        ' WHERE symbol = "_SPY"'
    ).fetchall()
    historical_portfolio_performance = db.execute(
        'SELECT date, symbol, cum_return'
        ' FROM historical_performance'
        ' WHERE symbol = "__BERI"'
    ).fetchall()
    print(historical_spy_performance)
    print(historical_portfolio_performance)
    return render_template('performance/portfolio.html', active='home')