import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def make_dicts(cur, row):
    return dict((cur.description[idx][0], value)
                for idx, value in enumerate(row))

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            "data.db",
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = make_dicts

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def query_db(query, args=(), one=False, commit=False):
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    if commit:
        db.commit()
    cur.close()
    close_db()
    return (rv[0] if rv else None) if one else rv


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)