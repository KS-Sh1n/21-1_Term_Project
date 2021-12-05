import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from .scraper import update_feed
from .db import _instance_path
from .insert import get_checked_site

db_location = ""

def init_scheduler():
    # APScheduler Configuration
    jobstores = {
        'default' : SQLAlchemyJobStore(url = 'db_location')
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
        template_folder='main/templates',
        instance_relative_config=True)

    # Development Config
    app.config.from_mapping(
        ENV = 'development', 
        DEBUG= True,
        DATABASE = os.path.join(_instance_path, 'data.db'),
        )
    app.secret_key = 'dev'
    
    # Production config
    #app.config.from_pyfile('prodconfig.py', silent=True)
    
    # SQLAlchemy congifuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'db_url'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    alc_db = SQLAlchemy(app)
    alc_db.Model.metadata.reflect(bind=alc_db.engine)

    # SQLAlchemy feed Database
    try:
        class Feed(alc_db.Model):
            __table__ = alc_db.Model.metadata.tables["sitefeed"]
            item_per_page = 10
    except:
        print("No Table")
    
    # Initialize database, blueprint, and scheduler
    from . import db, insert, auth
    alc_db.init_app(app)
    db.init_app(app)
    app.register_blueprint(insert.bp)
    app.register_blueprint(auth.bp)
    scheduler = init_scheduler()

    # Main page template
    @app.route("/", methods=['GET', 'POST'])
    def index():
        con = db.get_db()
        cur = con.cursor()
        sitefeed_result= []
        work = ""

        # Check admin or guest
        if "admin" in session:
            status = "admin"
        else:
            status = "guest"

        # Scheduler to scrape feed at every 0 / 30 minute
        scheduler.add_job(
        func= update_feed,
        trigger= 'cron',
        minute = "0, 30",
        id = "scrape",
        replace_existing= True)

        sorting = request.args.get('sort', "latest")
        page = request.args.get('page', 1, type=int)

        # Update color
        sitedata_color_list = cur.execute("SELECT sitename, sitecolor FROM sitedata").fetchall()
        for feed in Feed.query.all():
            for color in sitedata_color_list:
                if feed.sitename == color[0] and feed.sitecolor != color[1]:
                    feed.sitecolor = color[1]
        alc_db.session.commit()

        # Get feed from table with pagination & sorting method
        if sorting == "latest":
            sitefeed_result= Feed.query.order_by(Feed.postdate.desc()).paginate(page, Feed.item_per_page, False)
        elif sorting == "name":
            sitefeed_result= Feed.query.order_by(Feed.sitename, Feed.postdate.desc()).paginate(page, Feed.item_per_page, False)
        elif sorting == "type":
            sitefeed_result= Feed.query.order_by(Feed.sitetype, Feed.sitename, Feed.postdate.desc()).paginate(page, Feed.item_per_page, False)
        else:
            sitefeed_result="No Data"
        alc_db.session.commit()

        if request.method == 'POST':
            try:
                # Scrape button to get feeds from website
                if "scrape" in request.form:
                    work = update_feed()
                    flash(work, 'success')
                    con.commit()
                    return redirect(url_for("index"))

                    '''
                    update_feed()
                    con.commit()
                    flash("Feeds have been updated")
                    return redirect(url_for("index"))
                    '''

                # Delete button to remove feeds from table
                # Appears after select button is clicked
                elif "delete" in request.form:
                    print(request.form)
                    cur.executemany("DELETE FROM sitefeed WHERE link in (?)", get_checked_site(request.form))
                    con.commit()
                    flash("Feeds have been deleted.")
                    return redirect(url_for("index"))

            # Error message if any error occured
            except Exception as e:
                msg = (str(e))
                flash(msg)

        # Apply change and close connection
        con.commit()
        cur.close()
        con.close()

        # Return template page
        return render_template('main.html', sitefeed = sitefeed_result, page = page, sorting = sorting, status = status, work = work)

    return app