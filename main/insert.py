from flask import Blueprint, flash, render_template, request, redirect, url_for
from .db import get_db, site_data_query, site_feed_query

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
        if value not in ("add", "alter", "on"):
            yield value
        elif value == "on":
            yield 1 
            break
        else:
            yield 0
            break

@bp.route('/', methods=['GET', 'POST'])
def insert():
    con = get_db()
    cur = con.cursor()    
    sitedata_result= []
    msg = "No Error"

    if request.method == 'POST':
        try:
            # Add sitedata table elements
            if "add" in request.form:
                # Create table if not exists
                cur.execute(site_data_query)
                cur.execute(site_feed_query)

                cur.executemany("INSERT INTO sitedata VALUES "
                    "(?, ?, ?, ?, ?, ?, ?, ?, ?)", [tuple(insert_value(request.form.values()))])
                con.commit()

                flash("success")
                # redirect to "end" the form (fresh state)
                return redirect(url_for("insert.insert")) 

            # Delete sitedata table elements
            elif "delete" in request.form:
                # want not to execute when no site has been selected.
                cur.executemany("DELETE FROM sitedata WHERE sitename in (?)", get_checked_site(request.form))
                con.commit()
                flash("sites has been deleted.")
                return redirect(url_for("insert.insert"))
            
            # Modify table elements (delete and recreate)
            elif "alter" in request.form:
                checked_site = tuple(get_checked_site(request.form))

                if len(checked_site) == 0:
                    flash("select a site to modify")
                elif len(checked_site) != 1:
                    flash("select only one site to modify")
                else:
                    site_backup = cur.execute("SELECT * FROM sitedata WHERE sitename = ?", *checked_site).fetchall()

                    form_values = list(request.form.values())
                    for i in range(len(form_values)):
                        if form_values[i] == "":
                            form_values[i] = site_backup[0][i]

                    # Delete table, and
                    # Reaplce it with a table with modified values
                    cur.execute("DELETE FROM sitedata WHERE sitename = ?", checked_site[0])
                    cur.executemany("INSERT INTO sitedata VALUES "
                        "(?, ?, ?, ?, ?, ?, ?, ?, ?)", [tuple(insert_value(form_values))])
                    con.commit()
                    flash("successfully modified a table.")

                return redirect(url_for("insert.insert"))

            # Delete every data
            elif "reset" in request.form:
                cur.execute("DROP TABLE sitedata")
                cur.execute("DROP TABLE sitefeed")
                con.commit()
                flash("successfully deleted every table.")
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