import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from flask import Flask, render_template, request, redirect, url_for, flash
from .scraper import update_feed
from .db import _instance_path
from .insert import get_checked_site

def init_scheduler():
    # APScheduler Configuration
    jobstores = {
        'default' : SQLAlchemyJobStore(url = 'sqlite:///instance/data.db')
    }
    executors = {
        'default' : ThreadPoolExecutor(20)
    }
    scheduler = BackgroundScheduler(jobstores = jobstores,  executors = executors)
    scheduler.start()
    return scheduler
def init_app():
    # Core application configuration
    app = Flask('__name__',
        static_folder= "main/static",
        template_folder='main/templates')
    app.config.from_mapping(
        ENV = 'development', 
        DEBUG= True,
        DATABASE = os.path.join(_instance_path, 'data.db')
        )
    app.secret_key = 'dev'

    # Initialize database, blueprint, and scheduler
    from . import db, insert
    db.init_app(app)
    app.register_blueprint(insert.bp)
    scheduler = init_scheduler()

    # Main page template
    @app.route('/', methods=['GET', 'POST'])
    def index():
        con = db.get_db()
        cur = con.cursor()
        sitefeed_result= []
        msg = ""

        # Scheduler to scrape feed at every 0 / 30 minute
        scheduler.add_job(
        func= update_feed,
        trigger= 'cron',
        minute = "0, 30",
        id = "scrape",
        replace_existing= True)

        try:
            # Display feeds at page
            sitefeed_result= cur.execute("SELECT * FROM sitefeed ORDER BY postdate DESC").fetchall()
            con.commit()
            msg = "No Error."

            # Scrape button to get feeds from website
            if "scrape" in request.form:
                update_feed()
                con.commit()
                return redirect(url_for("index"))

            # Delete button to remove feeds from table
            # Appears after select button is clicked
            elif "delete" in request.form:
                print(request.form)
                cur.executemany("DELETE FROM sitefeed WHERE link in (?)", get_checked_site(request.form))
                con.commit()
                flash("feeds have been deleted.")
                return redirect(url_for("index"))

        # Error message if any error occured
        except Exception as e:
            msg = (str(e))

        # Apply change and close connection
        con.commit()
        cur.close()
        con.close()

        # Return template page
        return render_template('base.html', sitefeed= sitefeed_result, msg = msg)
    return app