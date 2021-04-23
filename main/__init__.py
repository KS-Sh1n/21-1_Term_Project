import os
from datetime import datetime
from flask import current_app, Flask, render_template, request, redirect, url_for

# To import from scraper application
Instance_Path= 'C:/Users/yunse/Desktop/Python/21-1_Term_Project/instance'

def init_app():
    # Initialize Core Application
    app = Flask('__name__',
        instance_path= Instance_Path,
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
    
    # Initialize Database & blueprint
    from . import db, insert
    db.init_app(app)
    app.register_blueprint(insert.bp)
    
    # A test page for hello world
    @app.route('/', methods=['GET', 'POST'])
    def index():
        con = db.get_db()
        cur = con.cursor()
        sitefeed_result= []
        msg = ""
        time = datetime.now().strftime("%Y/%m/%d %H:%M")

        try:
            sitefeed_result= cur.execute("SELECT * FROM sitefeed ORDER BY postdate DESC").fetchall()
            con.commit()
            msg = "No Error."
        except Exception as e:
            msg = (str(e))

        con.commit()
        cur.close()
        con.close()
        return render_template('base.html', sitefeed= sitefeed_result, msg = msg, time = time)
    return app