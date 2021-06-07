from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db, auth_data_query

# Declare blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/', methods=['GET', 'POST'])
def auth():
    con = get_db()
    cur = con.cursor()    
    if "admin" in session:
        session.clear()
        flash("Admin mode deactivated")
        return redirect(url_for("index"))
    else:
        if request.method == 'POST':
            try:
                # Create authdata table if not exists
                cur.execute(auth_data_query)

                admin_code_from_db = con.execute("SELECT * from authdata").fetchall()
                admin_code = request.form['admincode']

                if admin_code == "":
                    flash("Admin code should not be empty")
                    return redirect(url_for("auth.auth"))
                elif not check_password_hash(admin_code_from_db[0][0], admin_code):
                    flash("Incorrect admin code. Try again")
                    return redirect(url_for("auth.auth"))
                else:
                    flash("Admin mode activated")
                    session["admin"]="Yes"
                    return redirect(url_for("index"))

            except Exception as e:
                msg = str(e)
                flash(msg)

        cur.close()
        con.close()
        return render_template('auth.html')