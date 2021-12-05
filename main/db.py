import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

_instance_path = ''

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config['DATABASE'])
    return db

@click.command('init-db')
@with_appcontext
def init_db_command():
    get_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_connection)
    app.cli.add_command(init_db_command)

def close_connection(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

site_data_query = (
    "CREATE TABLE IF NOT EXISTS sitedata "
    "(sitename TEXT NOT NULL PRIMARY KEY," 
    "main_address TEXT NOT NULL,"
    "scrape_address TEXT NOT NULL,"
    "sitetype TEXT NOT NULL,"
    "link_query TEXT NOT NULL,"
    "postnum_query INTEGER NOT NULL,"
    "title_query TEXT NOT NULL,"
    "author_query TEXT NOT NULL,"
    "sitecolor TEXT NOT NULL,"
    "js_included INTEGER)")

site_feed_query = (
    "CREATE TABLE IF NOT EXISTS sitefeed "
    "(sitename TEXT NOT NULL," 
    "sitetype TEXT NOT NULL,"
    "postdate TEXT NOT NULL,"
    "postnum INTEGER NOT NULL,"
    "title TEXT NOT NULL,"
    "author TEXT NOT NULL,"
    "link TEXT NOT NULL PRIMARY KEY,"
    "sitecolor TEXT NOT NULL,"
    "FOREIGN KEY(sitename) REFERENCES sitedata(sitename))")

auth_data_query = (
    "CREATE TABLE IF NOT EXISTS authdata "
    "(admincode TEXT NOT NULL PRIMARY KEY)")