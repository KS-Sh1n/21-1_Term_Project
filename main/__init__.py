import os
from flask import current_app, Flask, render_template, request, redirect, url_for

def init_app():
    # Initialize Core Application
    app = Flask('__name__',
        instance_path= 'C:/Users/yunse/Desktop/Python/21-1_Term_Project/instance',
        template_folder='main/templates')
    app.config.from_mapping(
        ENV = 'development',
        SECERT_KEY= 'dev',
        DEBUG= True,
        DATABASE = os.path.join(app.instance_path, 'data.db')
    )

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize Database & blueprint
    from . import db, result
    db.init_app(app)
    app.register_blueprint(result.bp)

    # A test page for hello world
    @app.route('/', methods=['GET', 'POST'])
    def index():
        msg1 = ""
        msg2 = ""
        msg3 = ""

        con = db.get_db()
        cur = con.cursor()
        if request.method == 'POST':
            try:                
                    sitename = request.form['sitename']
                    main_address = request.form['main_address']
                    scrape_address = request.form['scrape_address']
                    sitetype = request.form['sitetype']
                    list_query = request.form['list_query']
                    link_query = request.form['link_query']
                    postnum_query = request.form['postnum_query']
                    title_query = request.form['title_query']
                    author_query = request.form['author_query']
                    if request.form.get('js_included'):
                        js_included = True
                    else:
                        js_included = False
                    
                    if "add" in request.form:
                        # To check if there is a sitedata table
                        if cur.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='sitedata'"
                        ).fetchone() is None:
                            cur.execute(db.create_site_data())
                        else:
                            msg1 = "Exists"
                        # To check if sitename is stored in sitedata
                        if cur.execute(
                        "SELECT * FROM sitename WHERE sitename = ?", (sitename,)
                        ).fetchall() is None:
                            cur.execute("INSERT INTO sitedata VALUES "
                            "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                            sitename, main_address, scrape_address, sitetype, list_query, link_query, postnum_query, title_query, author_query, js_included))
                        else:
                            msg1 = "Sitedata Exists but Same sitename."
                        
                        # To check if there is a sitedata table
                        if cur.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (sitename,)
                        ).fetchone() is None:
                            print("a")
                            #cur.execute(create_site_feed(sitename, sitetype))
                        else:
                            msg2 = "Same sitefeed Table Exists."

                        msg3 = "No Error."

                        # redirect to "end" the form (fresh state)
                        return redirect(url_for("index"))
                    
                    elif "delete" in request.form:
                        msg1 = request.form
                        return redirect(url_for("index")) 

                    elif "alter" in request.form:
                        msg1 = "hmm"
                        return redirect(url_for("index"))

            except Exception as e:
                msg3 = str(e)

        con.commit()
        cur.close()
        con.close()
        return render_template('base.html',msg1= msg1, msg2= msg2, msg3= msg3)

    return app