from flask import (Blueprint, flash, g, render_template, request, session, url_for)
from main.db import get_db

bp = Blueprint('result', __name__, url_prefix='/result')

@bp.route('/', methods=['GET', 'POST'])
def result():
    con = get_db()
    cur = con.cursor()
    sitedata_result= []
    sitefeed_result= []

    try:
        sitename = "khu_general"
        sitedata_result= cur.execute("SELECT * FROM sitedata").fetchall()
        if sitedata_result is None:
            sitedata_result = ["No Result."]

        sitefeed_result= cur.execute("SELECT * FROM ?", (sitename,)).fetchall()
        if sitefeed_result is None:
            sitefeed_result = ["No Result."]

        con.commit()

    except Exception as e:
        return(str(e))

    finally:
        cur.close()
        con.close()
        return render_template('result.html', result1 = sitedata_result, result2= sitefeed_result)