import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
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
        DATABASE = os.path.join(_instance_path, 'data.db'),
        )
    app.secret_key = 'dev'
    
    # SQLAlchemy congifuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    alc_db = SQLAlchemy(app)
    alc_db.Model.metadata.reflect(bind=alc_db.engine)

    # SQLAlchemy feed Database
    class Feed(alc_db.Model):
        __table__ = alc_db.Model.metadata.tables["sitefeed"]
        item_per_page = 10
    
    # Initialize database, blueprint, and scheduler
    from . import db, insert
    alc_db.init_app(app)
    db.init_app(app)
    app.register_blueprint(insert.bp)
    scheduler = init_scheduler()

    # Main page template
    @app.route("/", methods=['GET', 'POST'])
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

        page = request.args.get('page', 1, type=int)
        sitefeed_result= Feed.query.order_by(Feed.postdate.desc()).paginate(page, Feed.item_per_page, False)
        alc_db.session.commit()

        if request.method == 'POST':
            try:
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
                '''
                #Sotring methods
                elif "date" in request.form:
                    sitefeed_result= Feed.query.order_by(Feed.postdate.desc()).paginate(page, Feed.item_per_page, False)
                    alc_db.session.commit()
                elif "name" in request.form:
                    sitefeed_result= Feed.query.order_by(Feed.sitename,Feed.postdate.desc()).paginate(page, Feed.item_per_page, False)
                    alc_db.session.commit()
                elif "type" in request.form:
                    sitefeed_result= Feed.query.order_by(Feed.sitetype,Feed.sitename,Feed.postdate.desc()).paginate(page, Feed.item_per_page, False)
                    alc_db.session.commit()
                '''
            # Error message if any error occured
            except Exception as e:
                msg = (str(e))
                print(msg)

        # Apply change and close connection
        con.commit()
        cur.close()
        con.close()

        # Return template page
        return render_template('main.html', msg = msg, sitefeed= sitefeed_result)

    return app