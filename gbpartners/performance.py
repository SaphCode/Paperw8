from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from gbpartners.db import get_db

import json
import datetime
from itertools import groupby

bp = Blueprint('performance', __name__)


@bp.route('/')
def index():
    db = get_db()
    
    query = db.execute('SELECT CAST(strftime("%Y", MIN(date)) AS INTEGER) as min_year, CAST(strftime("%Y", MAX(date)) AS INTEGER) as max_year'
        ' FROM historical_performance'
    ).fetchone()
    
    years = [query['min_year'] + i for i in range(query['max_year']-query['min_year']+1)]
    
    query = db.execute('SELECT name, strftime("%Y", date) AS year, strftime("%m-%d", date) as month_day, cum_return'
        ' FROM historical_performance'
        ' GROUP BY name, year'
        ' HAVING MIN(month_day)' 
        ' ORDER BY month_day ASC'
    ).fetchall()
    results = {row['name']: (row['year']+'-'+row['month_day'], row['cum_return']) for row in query} # yyyy-mm-dd
    annualized_returns = {}
    for bm in results:
        annualized_returns[bm] = {}
        for previous,current in zip(bm, bm[1:]):
                start_date = datetime.strptime('%Y-%m-%d', previous[0])
                end_date = datetime.strptime('%Y-%m-%d', current[0])
                delta = end_date - start_date
                annualized_returns[bm][datetime.strptime('%Y', previous[0])] = (current[1]-previous[1])/previous[1]
    
    
    return render_template('performance/portfolio.html', active='home', years=years)