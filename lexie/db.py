import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """open db"""
    if 'db' not in g:
        g.db = sqlite3.connect( #pylint:disable=assigning-non-slot
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None): #pylint:disable=unused-argument,invalid-name
    """close db"""
    database = g.pop('db', None)
    if database is not None:
        database.close()

def init__db(): #pragma: nocover
    """ build db from schema"""
    database = get_db()
    with current_app.open_resource('schema.sql') as schema_file:
        database.executescript(schema_file.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command(): # pragma: nocover
    """ Clear existing data and create new tables """
    init__db()
    click.echo('Database initialized')

def init_app(app):
    """ initialize application with db"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
