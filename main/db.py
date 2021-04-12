import sqlite3
import click
from flask import current_app, g, request
from flask.cli import with_appcontext

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config['DATABASE'])
    return db

def init_db():
    with current_app.app_context():
        db = get_db()

def create_site_feed(sitename, type):

    site_feed_query = (
        "CREATE TABLE {0} ".format(sitename) +
        "(ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
        "sitename TEXT DEFAULT " + sitename +  "," 
        "type TEXT DEFAULT " + type +  ","
        "postdate TEXT,"
        "postnum INTEGER,"
        "title TEXT,"
        "author TEXT,"
        "link TEXT)")
    return site_feed_query

def create_site_data():
    
    site_data_query = (
        "CREATE TABLE sitedata "
        "(sitename TEXT ," 
        "main_address TEXT ,"
        "scrape_address TEXT,"
        "sitetype TEXT,"
        "list_query TEXT,"
        "link_query TEXT,"
        "postnum_query INTEGER,"
        "title_query TEXT,"
        "author_query TEXT,"
        "js_included INTEGER)")
    return site_data_query

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_connection)
    app.cli.add_command(init_db_command)

def close_connection(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()