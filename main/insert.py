from flask import Blueprint, flash, render_template, request, redirect, url_for
from .db import get_db, site_data_query, site_feed_query
from .scraper import test_feed

# Declare blueprint
bp = Blueprint('insert', __name__, url_prefix='/insert')

def get_checked_site(form_):
    """ (multidict) -> generator
    Retrieve checked data from request.form multidict.

    if value of request.form is "on", which means checkbox is checked, get a corresponding key with a form of single-length tuple. Then this generator is handed into executemany() function to perform operation with checked data.

    >>> get_checked_site({"a": "on", "b": "", "c": "on"})
    generator of ("a", ), ("c", )
    """
    for key_value in form_.items():
        try:
            if key_value[1] == "on" and key_value[0] != "js_included":
                yield (key_value[0], )
            else:
                continue
        except:
            return
def insert_value(form_value):
    """ (tuple) -> generator
    Retireve addsite form value from request.form

    This function reads data until it reaches data whose value is "add", "alter" or "on"
    If "on" is in the request.form, it means that checkbox in the addsite form has been checked. The function yields 1(true) in this case, to indicate that checkbox has been checked and 0(false) otherwise.

    >>> insert_value("a", "b", "c", "on", "add")
    generator of ("a", "b", "c", 1)
    """
    for value in form_value:
        if value == "on":
            yield "Yes"
            break
        elif value in ("", "Yes", "No"):
            yield "No"
            break
        else:
            yield value

def uniqueness_test(form_tuple, ref_tuple):
    for form in form_tuple:
        for ref in ref_tuple:
            if form in ref:
                return True
    return False

@bp.route('/', methods=['GET', 'POST'])
def insert():
    con = get_db()
    cur = con.cursor()    
    sitedata_result= []
    msg = "No Error"

    if request.method == 'POST':
        try:
            print(request.form)
            # Add sitedata table elements
            if "add" in request.form:
                # Create table if not exists
                cur.execute(site_data_query)
                cur.execute(site_feed_query)

                # Check if every element of form has been filled
                for i in request.form.items():
                    if (i[0] != "add" and i[1] == ""):
                        flash("Fill out every information to add site")
                        return redirect(url_for("insert.insert"))

                # Check for uniqueness of sitename
                if uniqueness_test((request.form["sitename"],request.form["sitecolor"]), cur.execute("SELECT sitename, sitecolor FROM sitedata").fetchall()):
                    flash("Sitename and Sitecolor must be unique per sitedata in table.")
                    return redirect(url_for("insert.insert"))

                # Test scraping to assess validity
                test = test_feed(request.form)
                if test != "success":
                    flash(test)
                else:
                    cur.executemany("INSERT INTO sitedata VALUES "
                    "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [tuple(insert_value(request.form.values()))])
                    flash("Site has been added")
                    con.commit()

                # redirect to "end" the form (fresh state)
                return redirect(url_for("insert.insert")) 

            # Delete sitedata table elements
            elif "delete" in request.form:
                # want not to execute when no site has been selected.
                cur.executemany("DELETE FROM sitedata WHERE sitename in (?)", get_checked_site(request.form))
                con.commit()
                flash("Sites have been deleted.")
                return redirect(url_for("insert.insert"))
            
            # Modify table elements (delete and recreate)
            elif "alter" in request.form:
                checked_site = tuple(get_checked_site(request.form))

                if len(checked_site) == 0:
                    flash("Select a site to modify")
                elif len(checked_site) != 1:
                    flash("Select only one site to modify")
                else:
                    site_backup = cur.execute("SELECT * FROM sitedata WHERE sitename = ?", *checked_site).fetchall()

                    form_values = list(request.form.values())
                    for i in range(len(site_backup[0])):
                        if form_values[i] == "":
                            form_values[i] = site_backup[0][i]

                    # Delete table, and
                    # Reaplce it with a table with modified values
                    cur.execute("DELETE FROM sitedata WHERE sitename = ?", checked_site[0])
                    cur.executemany("INSERT INTO sitedata VALUES "
                        "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [tuple(insert_value(form_values))])
                    con.commit()
                    flash("Successfully modified a table.")

                return redirect(url_for("insert.insert"))

            # Delete every data
            elif "reset" in request.form:
                cur.execute("DROP TABLE sitedata")
                cur.execute("DROP TABLE sitefeed")
                con.commit()

        except Exception as e:
            msg = str(e)
            flash(msg)

    if (cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' and name = 'sitedata'")).fetchone() is not None:
        sitedata_result= cur.execute("SELECT * FROM sitedata ORDER BY sitename").fetchall()

    con.commit()
    cur.close()
    con.close()
    return render_template('insert.html', sitedata = sitedata_result)