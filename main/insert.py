from flask import (Blueprint, flash, g, render_template, request, session, redirect, url_for)
from main.db import get_db, insert_feed_query, site_data_query, site_feed_query

bp = Blueprint('insert', __name__, url_prefix='/insert')

@bp.route('/', methods=['GET', 'POST'])
def insert():
    con = get_db()
    cur = con.cursor()    
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
            if request.form.get('js_included'):
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
                results = cur.execute("SELECT * FROM sitedata WHERE sitename = ?", (sitename,)).fetchall()

                # redirect to "end" the form (fresh state)
                flash("Success.")
                for result in results:
                    flash(result)
                return redirect(url_for("insert.insert")) 
            
            elif "delete" in request.form:
                cur.execute("DELETE FROM sitedata")
                cur.execute("DELETE FROM sitefeed")
                con.commit()
                flash("Successfully delete data from tables.")
                return redirect(url_for("insert.insert")) 

            elif "reset" in request.form:
                cur.execute("DROP TABLE sitedata")
                cur.execute("DROP TABLE sitefeed")
                con.commit()
                flash("Successfully delete every table.")
                return redirect(url_for("insert.insert"))

        except Exception as e:
            msg = str(e)

    con.commit()
    cur.close()
    con.close()
    return render_template('insert.html',msg= msg)

@bp.route('/feed', methods=['GET', 'POST'])
def insert_feed():
    con = get_db()
    cur = con.cursor()
    msg = "No Error"

    if request.method == "POST":
        try:
            sitename = request.form['sitename']
            sitetype = request.form['sitetype']
            postdate = request.form['postdate']
            postnum = request.form['postnum']
            title = request.form['title']
            author = request.form['author']
            link = request.form['link']
            
            insert_tuple = (
                sitename, sitetype, postdate, postnum, title, author, link)

            if "add" in request.form:
                cur.execute(insert_feed_query, insert_tuple)
                return redirect(url_for("insert.insert/feed"))

            elif "delete" in request.form:
                cur.execute("DELETE FROM sitefeed WHERE id >= 1")
                return redirect(url_for("insert.insert/feed"))

        except Exception as e:
            msg = str(e)
    
    con.commit()
    cur.close()
    con.close()

    return render_template('insert_feed.html', msg = msg)