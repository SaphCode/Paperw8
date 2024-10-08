import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

from werkzeug.security import generate_password_hash

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('database\schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def create_user(username, password):
    db = get_db()
    
    db.execute(
        'INSERT into user(display_name, username, password) VALUES(?, ?, ?)',
        (username.capitalize(), username, generate_password_hash(password))
    )
    db.commit()

@click.command('create-user')
@click.argument('username')
@click.argument('password')
@with_appcontext
def create_user_command(username, password):
    """Inserts a user with the given username and password into the db."""
    create_user(username, password)
    click.echo(f'Created user {username}')
    

def delete(table_name, identifier):
    if identifier:
        return
    else:
        raise Exception('No identifier given.')

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def insert_sample_db_command():
    """Inserts sample data into the database."""
    db = get_db()
    

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_user_command)