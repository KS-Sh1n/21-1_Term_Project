import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from .scraper import update_feed
from .db import _instance_path

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
    # Initialize Core Application
    app = Flask('__name__',
        instance_path= _instance_path,
        static_folder= "main\static",
        template_folder='main/templates')
    app.config.from_mapping(
        ENV = 'development', 
        DEBUG= True,
        DATABASE = os.path.join(app.instance_path, 'data.db')
        )
    app.secret_key = 'dev'

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database & blueprint
    from . import db, insert
    db.init_app(app)
    app.register_blueprint(insert.bp)
    scheduler = init_scheduler()

    # Main page with sitefeed data
    @app.route('/', methods=['GET', 'POST'])
    def index():
        con = db.get_db()
        cur = con.cursor()
        sitefeed_result= []
        msg = ""
        time = datetime.now().strftime("%Y/%m/%d %H:%M")

        # Scheduler to scrape feed at every 0 / 30 minute
        # Server automatically scrapes feed when server is loaded for the first time by a user.
        scheduler.add_job(
        func= update_feed,
        trigger= 'cron',
        minute = "0, 30",
        id = "scrape",
        replace_existing= True)

        try:
            sitefeed_result= cur.execute("SELECT * FROM sitefeed ORDER BY postdate DESC").fetchall()
            con.commit()
            msg = "No Error."

            # Scrape feeds
            if "scrape" in request.form:
                update_feed()
                con.commit()
                return redirect(url_for("index"))

        except Exception as e:
            msg = (str(e))

        con.commit()
        cur.close()
        con.close()
        return render_template('base.html', sitefeed= sitefeed_result, msg = msg, time = time)
    return app