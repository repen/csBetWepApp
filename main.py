from flask import Flask, render_template, request
import os, json, re, pickle
from Model import CSGame, Market, Fixture
from bs4 import BeautifulSoup
from datetime import datetime
from Globals import WORK_DIR
from tools import hash_, listdir_fullpath

app = Flask(__name__)



@app.route('/')
def index():
    data = {}
    data['fixtures'] = []
    
    current_time = datetime.now().timestamp()
    date = request.args.get('date', default=False)
    
    if date:
        date = datetime.strptime(date, "%m/%d/%Y").timestamp()
        fixtures = CSGame.select().where( (date < CSGame.m_time) & (CSGame.m_time < date + 87000))
    else:
        fixtures = CSGame.select().where( CSGame.m_time < current_time + 87000 )
    
    for fixture in fixtures:
        m_id = fixture.m_id
        m_team = "{} vs {}".format( fixture.team1, fixture.team2 )
        m_time = datetime.fromtimestamp( fixture.m_time ).strftime("%Y.%m.%d %H:%M")
        data['fixtures'].append( ( m_id, m_team, m_time) )

    return render_template("index.html", data = data)

@app.route('/match/<m_id>')
def match_page(m_id):
    data = {}
    # return render_template("match.html", data = data)
    path_id = WORK_DIR + "/data/objects/" + hash_(m_id)
    l_objs = listdir_fullpath( WORK_DIR + "/data/objects" )
    if path_id in l_objs:
        
        with open(path_id, "rb") as f:
            fixture = pickle.load(f)
        
        data['name_markets'] = sorted( list( fixture.name_markets ) )
        return render_template("match.html", data = data)
    
    else:
        return "Not path_id " + m_id 

@app.route('/filter')
def filter_page():
    data = {}
    return render_template("filter.html", data = data)



if __name__ == '__main__':
    if os.getenv("APP_PATH", False):
        app.run()
    else:
        app.run(port=5010, host='0.0.0.0', debug=True)
