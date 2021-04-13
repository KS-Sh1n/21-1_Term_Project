from flask import (Blueprint, flash, g, render_template, request, session, url_for)
from main.db import get_db

bp = Blueprint('result', __name__, url_prefix='/result')

@bp.route('/', methods=['GET', 'POST'])
def result():
    return "What to post"