from flask import Flask, render_template, request
import os, json, re
from Model import CSGame
from bs4 import BeautifulSoup
from datetime import datetime
from Globals import WORK_DIR

app = Flask(__name__)



@app.route('/')
def index():
    data = {}
    select_time = datetime.now().timestamp()
    date = request.args.get('date', default=False)
    print(date)
    return render_template("index.html", data = data)

@app.route('/match/<m_id>')
def match_page(m_id):
    data = {}
    # return render_template("match.html", data = data)
    return "m_id: " + m_id


if __name__ == '__main__':
    if os.getenv("APP_PATH", False):
        app.run()
    else:
        app.run(port=5010, host='0.0.0.0', debug=True)
