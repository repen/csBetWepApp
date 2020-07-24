from flask import Flask, render_template, request
import os, json, re, pickle
from Model import CSGame
from objbuild import Market, Fixture
from bs4 import BeautifulSoup
from datetime import datetime
from Globals import WORK_DIR
from tools import hash_, listdir_fullpath, get_search
import itertools

app = Flask(__name__)

@app.context_processor
def utility_processor():
    def search_markets(array, name):
        result = False
        array = [x for x in array if x.name == name]
        if array:
            result = array[0]
        return result

    def time_human(timestamp):
        return datetime.fromtimestamp( timestamp ).strftime("%Y.%m.%d %H:%M")

    return dict(search_markets=search_markets, time_human=time_human)

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

def prepare_date(string):
    start = string.split(":")[0]
    end = string.split(":")[1]
    return (datetime.strptime(start, "%Y-%m-%d").timestamp(), datetime.strptime(end, "%Y-%m-%d").timestamp())

@app.route('/filter')
def filter_page():
    data = {}
    data['result'] = []
    params = request.args.to_dict()
    
    fixtures = []
    l_objs = listdir_fullpath( WORK_DIR + "/data/objects" )


    for path in l_objs:
        
        with open(path, "rb") as f:
            fixture = pickle.load(f)
        fixtures.append( fixture )

    if params:
        {
        'time': '2020-07-21:2020-07-22', 'name_market': '', 
        't1name': '', 't2name': '', 'sum_t1': '100', 'sum_t2': '100', 'num_snapshot': '5'}
        params['time'] = prepare_date( params['time'] )
        params['sum_t1'] = int( params['sum_t1'] )
        params['sum_t2'] = int( params['sum_t2'] )
        params['num_snapshot'] = int( params['num_snapshot'] )
        query = get_search(params, fixtures)
        
        # for q in query:
        #     for e, m in enumerate( q.markets):
        #         if not m:
        #             q.markets.pop(e)

        data['result'] = query
        data['params'] = params
        # print(query[0].markets[-5], "!!!")


    data["name_markets"] = set( itertools.chain.from_iterable( [x.name_markets for x in fixtures] ) )
    data["teams"] = set( itertools.chain.from_iterable( [ [x.team01, x.team02] for x in fixtures] ) )

    return render_template("filter.html", data = data)



if __name__ == '__main__':
    if os.getenv("APP_PATH", False):
        app.run()
    else:
        app.run(port=5010, host='0.0.0.0', debug=True)
