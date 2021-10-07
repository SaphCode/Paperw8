from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from gbpartners.db import get_db

import json
from datetime import datetime, date
from itertools import tee

bp = Blueprint('performance', __name__)

def percent(number):
    return number/100

def unnest(d, keys=[]):
    result = []
    for k, v in d.items():
        if isinstance(v, dict):
            result.extend(unnest(v, keys + [k]))
        else:
            result.append(tuple(keys + [k, v]))
    return result

@bp.route('/')
def index():
    db = get_db()
    
    # find the first day of each year for which we got data
    query_first_of_year = db.execute('SELECT name, strftime("%Y", date) AS year, strftime("%m-%d", date) as month_day, cum_return'
        ' FROM historical_performance'
        ' GROUP BY name, year'
        ' HAVING MIN(month_day)' 
        ' ORDER BY month_day ASC'
    ).fetchall()
    
    # find the names of the benchmarks, to use for the list comp in the dict later
    query_names = db.execute('SELECT DISTINCT name FROM historical_performance').fetchall()
    
    # find the latest date of the current year, so that we can tell the return for now
    query_latest = db.execute('SELECT name, MAX(date) as date, cum_return'
        ' FROM historical_performance'
        ' GROUP BY name'
        ' ORDER BY name DESC'
    ).fetchall()
    
    
    date_format = '%Y-%m-%d' # parsing format for date
    
    last_year = datetime.strptime(query_latest[0]['date'], date_format).year # last year for which we got data
    
    # put it into the format {S&P: [(date, return), (date, return)], Portfolio: [...]}
    results = {row2['name']: [(datetime.strptime(row['year']+'-'+row['month_day'], date_format), row['cum_return']) for row in query_first_of_year if row['name'] == row2['name']] for row2 in query_names}
    # put the latest result in the same format
    results_latest = {row['name']: (datetime.strptime(row['date'], date_format), row['cum_return']) for row in query_latest}
    # add the latest result to the first of each year results
    for name in results_latest:
        results[name].append(results_latest[name])

    # annualize the returns by taking into account the days of the full year
    # & the days we have data for
    annualized_returns = {}
    for name in results:
        annualized_returns[name] = {}
        # sort so we get consecutive years
        results[name].sort(key=lambda r: r[0])
        
        # iterate over previous and current
        for prev, cur in zip(results[name], results[name][1:]):
            start_date = prev[0]
            end_date = cur[0]
            delta = end_date - start_date
            
            full_year_delta = date(end_date.year+1, 1, 1) - date(end_date.year, 1, 1)
            
            # we should not annualize, since we got full years, and if
            # the market is not open on december 31, that does not matter
            # the money will be compounded the next year and the return will be
            # reflected there
            # ---
            # for the latest year we also don't want to annualize since
            # that will exaggerate downswings & upswings
            annualized_return = (1 + percent(cur[1]))/(1 + percent(prev[1]))
            
            #if prev[0].year != last_year:
            #    annualized_return = annualized_return**(full_year_delta.days/delta.days)
            
            annualized_return_percent = (annualized_return-1)*100
            annualized_returns[name][prev[0]] = annualized_return_percent

    # put it into another structure for convenience
    annualized_returns = unnest(annualized_returns)
    # make it like so: {2020: [('S&P', return), ('Portfolio', return)]}
    annualized_returns = {datetime.strftime(s[1], '%Y'): [(t[0], t[2]) for t in annualized_returns if t[1] == s[1]] for s in annualized_returns}
    for year in annualized_returns:
        annualized_returns[year].sort(key=lambda t: t[0], reverse=True)
    
    return render_template('performance/portfolio.html', active='home', last_year=last_year, annualized_returns=annualized_returns)