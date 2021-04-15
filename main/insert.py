from flask import (Blueprint, flash, g, render_template, request, session, redirect, url_for)
from main.db import get_db, site_data_query, site_feed_query
from main.scraper import update_feed

bp = Blueprint('insert', __name__, url_prefix='/insert')

@bp.route('/', methods=['GET', 'POST'])
def insert():
    con = get_db()
    cur = con.cursor()    
    sitedata_result= []
    msg = "No Error"

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
            if "js_included" in request.form:
                js_included = True
            else:
                js_included = False
            
            form_tuple = (
                    sitename, main_address, scrape_address, sitetype, list_query, link_query, postnum_query, title_query, author_query, js_included)

            if "add" in request.form:
                
                for form in form_tuple:
                    if form == "":
                        flash("Plesae fill out every data.")
                        return redirect(url_for("insert.insert"))

                # Create sitedata table and sitefeed table
                cur.execute(site_data_query)
                cur.execute(site_feed_query)

                # To check if sitename is stored in sitedata
                if cur.execute(
                "SELECT sitename FROM sitedata WHERE sitename = ?", (sitename,)
                ).fetchone() is None:
                    cur.execute("INSERT INTO sitedata VALUES "
                    "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", form_tuple)
                else:
                    flash("Sitedata already exists.")
                    return redirect(url_for("insert.insert"))
                
                con.commit()

                # redirect to "end" the form (fresh state)
                flash("Success.")
                return redirect(url_for("insert.insert")) 
            
            elif "delete" in request.form:

                keys = list(request.form.keys())
                flash(keys)

                sitenames = cur.execute("SELECT sitename FROM sitedata WHERE sitename = ?", ['khu_general']).fetchall()
                
                for sitename in sitenames:
                    if sitename[0] not in keys:
                        flash(sitename[0])
                    else:
                        flash("123")
                
                return redirect(url_for("insert.insert")) 

            elif "reset" in request.form:
                cur.execute("DROP TABLE sitedata")
                cur.execute("DROP TABLE sitefeed")
                con.commit()
                flash("Successfully delete every table.")
                return redirect(url_for("insert.insert"))

        except Exception as e:
            msg = str(e)

    if (cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' and name = 'sitedata'")).fetchone() is not None:
        sitedata_result= cur.execute("SELECT * FROM sitedata ORDER BY sitename").fetchall()

    con.commit()
    cur.close()
    con.close()
    return render_template('insert.html', sitedata = sitedata_result, msg= msg)

@bp.route('/feed', methods=['GET', 'POST'])
def insert_feed():
    con = get_db()
    cur = con.cursor()
    msg = "No Error"

    if request.method == "POST":
        try:

            if "scrape" in request.form:
                update_feed()
                con.commit()
                return redirect(url_for("insert.insert_feed"))

            elif "delete" in request.form:
                cur.execute("DELETE FROM sitefeed WHERE id >= 1")
                con.commit()
                return redirect(url_for("insert.insert_feed"))

        except Exception as e:
            msg = str(e)
    
    con.commit()
    cur.close()
    con.close()

    return render_template('insert_feed.html', msg = msg)