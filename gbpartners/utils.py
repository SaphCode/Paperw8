import csv
import os
from datetime import datetime

def confirmation_required(desc_fn):
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.args.get('confirm') != '1':
                desc = desc_fn()
                return redirect(url_for('confirm', 
                    desc=desc, action_url=quote(request.url)))
            return f(*args, **kwargs)
        return wrapper
    return inner
    
def format_date(unformatted):
    print(unformatted)
    dt = datetime.strptime(unformatted, '%m/%d/%y')
    print(dt.strftime('%Y-%m-%d'))
    return dt.strftime('%Y-%m-%d')

def process_performance_file(upload_path, filename, db):
    performance_data = [line for line in open(os.path.join(upload_path, filename), 'r') if line.startswith('Cumulative')]
    edited_filename = 'edited_performance.csv'
    with open(os.path.join(upload_path, edited_filename), 'w') as f:
        for line in performance_data[1:]:
            f.write(line)
    
    with open(os.path.join(upload_path, edited_filename), 'r') as f:
        csvfile = csv.DictReader(f, delimiter=',')
        for row in csvfile:
            print(row)
            date = format_date(row['Date'])
            db.execute(
                "INSERT OR REPLACE"
                " INTO historical_performance (date, name, cum_return)"
                " VALUES (?, ?, ?)",
                (date, row['BM1'], row['BM1Return'])
            )
            db.execute(
                "INSERT OR REPLACE"
                " INTO historical_performance (date, name, cum_return)"
                " VALUES (?, ?, ?)",
                (date, row['BM2'], row['BM2Return'])
            )
            db.execute(
                "INSERT OR REPLACE"
                " INTO historical_performance (date, name, cum_return)"
                " VALUES (?, ?, ?)",
                (date, row['BM3'], row['BM3Return'])
            )
            db.execute(
                "INSERT OR REPLACE"
                " INTO historical_performance (date, name, cum_return)"
                " VALUES (?, ?, ?)",
                (date, 'PORTFOLIO', row['ConsolidatedReturn'])
            )
        db.commit()