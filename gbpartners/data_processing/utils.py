import csv
import os
from datetime import datetime
import json

from werkzeug.utils import secure_filename

def percent(number):
    return number/100

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
    dt = datetime.strptime(unformatted, '%m/%d/%y')
    return dt.strftime('%Y-%m-%d')

def upload_file(parent_dir, filename, file):
    if not os.path.exists(os.path.join(parent_dir, secure_filename(filename))):
        print(os.path.join(parent_dir, secure_filename(filename)))
        file.save(os.path.join(parent_dir, secure_filename(filename)))
    else:
        raise FileExistsError(f'File already exists: {secure_filename(filename)}')

def process_performance_file(upload_path, filename, db):
    performance_data = [line.rstrip().split(',') for line in open(os.path.join(upload_path, filename), 'r') if line.startswith('Cumulative')]
    edited_filename = 'edited_performance.csv'
    
    with open(os.path.join(upload_path, edited_filename), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(performance_data[1:])
    
    with open(os.path.join(upload_path, edited_filename), 'r') as f:
        csvfile = csv.DictReader(f, delimiter=',')
        
        # shift the returns to the origin
        # get the first row to base the next returns
        # on that first row
        first_row = next(csvfile)
        date = format_date(first_row['Date'])
        # INSERT FIRST ROW
        db.execute(
            "INSERT OR REPLACE"
            " INTO historical_performance (date, name, cum_return)"
            " VALUES (?, ?, ?)",
            (date, first_row['BM1'], 0)
        )
        # INSERT FIRST ROW
        db.execute(
            "INSERT OR REPLACE"
            " INTO historical_performance (date, name, cum_return)"
            " VALUES (?, ?, ?)",
            (date, 'PORTFOLIO', 0)
        )
        '''
        print(f'Old return:\t{first_row["BM1Return"]},\tNew return:\t0')
        print(f'Old return:\t{first_row["ConsolidatedReturn"]},\tNew return:\t0')
        '''
        for row in csvfile:
            date = format_date(row['Date'])
        
            # calculate new return
            new_return = (1 + percent(float(row['BM1Return'])))/(1 + percent(float(first_row['BM1Return'])))
            '''
            print(f'Old return:\t{row["BM1Return"]},\tNew return:\t{(new_return - 1)*100}')
            '''
            # convert to a percentage
            row['BM1Return'] = (new_return - 1)*100
            
            # INSERT
            db.execute(
                "INSERT OR REPLACE"
                " INTO historical_performance (date, name, cum_return)"
                " VALUES (?, ?, ?)",
                (date, row['BM1'], row['BM1Return'])
            )
            
            # calculate new return
            new_return = (1 + percent(float(row['ConsolidatedReturn'])))/(1 + percent(float(first_row['ConsolidatedReturn'])))
            # convert to a percentage
            new_return = (new_return - 1)*100
            '''
            #print(f'Old return:\t{row["ConsolidatedReturn"]},\tNew return:\t{(new_return - 1)*100}')
            '''
            # INSERT
            db.execute(
                "INSERT OR REPLACE"
                " INTO historical_performance (date, name, cum_return)"
                " VALUES (?, ?, ?)",
                (date, 'PORTFOLIO', new_return)
            )

        db.commit()
    

def sqllite_to_json(query_result):
    return json.dumps([dict(row) for row in query_result], default=str)