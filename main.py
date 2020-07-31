from flask import Flask, render_template, request
import os, json, re, pickle
from Model import CSGame
from objbuild import Market, Fixture
from bs4 import BeautifulSoup
from datetime import datetime
from Globals import WORK_DIR
from tools import hash_, listdir_fullpath, get_search
import itertools
from waitress import serve
# import logging
# logger = logging.getLogger('waitress')
# logger.setLevel(logging.INFO)
pattern01 = r"выигра\w+ \d+ раун\w+"

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

    def rename_market(market):

        result = None
        for name in market.keys():
            search = re.search( r"выигра\w+ одну карту", name)
            if search:
                result = name
                break

        return result

    return dict(search_markets=search_markets, time_human=time_human, rename_market=rename_market)

@app.route('/')
def index():
    data = {}
    data['fixtures'] = []
    data['hash_objs'] = list( map( lambda x:x.split("/")[-1] , listdir_fullpath( WORK_DIR + "/data/objects" ) ) )

    
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
        data['fixtures'].append( ( m_id, m_team, m_time, hash_( m_id )) )

    return render_template("index.html", data = data)

@app.route('/match/<m_id>')
def match_page(m_id):
    data = {}
    # return render_template("match.html", data = data)
    path_id = WORK_DIR + "/data/objects/" + hash_(m_id)
    l_objs = listdir_fullpath( WORK_DIR + "/data/objects" )
    if path_id in l_objs:
        try:
            with open(path_id, "rb") as f:
                fixture = pickle.load(f)
            data['name_markets'] = sorted( list( fixture.name_markets ) )
            data['team1'], data['team2'] = fixture.team01, fixture.team02
            data["result"] = fixture.markets[0]
            res_markets = {}
            first = fixture.markets[0]
            for x in first:
                res_markets[x] = first[x].winner
            
            data["result"] = res_markets
            print(res_markets)
            return render_template("match.html", data = data)
        except Exception as e:
            print("Error", str(e))
            return "Error: " + str(e)
    
    else:
        return "Not path_id " + m_id 

def convert_date(string):
    start = string.split(":")[0]
    end = string.split(":")[1]
    return (datetime.strptime(start, "%Y-%m-%d").timestamp(), datetime.strptime(end, "%Y-%m-%d").timestamp())

def name_markets_prepare(fixtures):
    pattern01 = r"выиграют одну карту|выиграет одну карту"
    def win_single_map(name_market):
        search = re.findall(pattern01, name_market)
        if search:
            # print(name_market, search)
            name_market = "выиграют одну карту"
        
        return name_market
    
    name_markets = set( itertools.chain.from_iterable( [x.name_markets for x in fixtures] ) )
    name_markets = set( map(win_single_map , name_markets ) )

    name_markets = sorted( name_markets )
    
    return name_markets

@app.route('/filter')
def filter_page():
    data = {}
    data['result'] = []
    params = request.args.to_dict()
    print("Filter")
    fixtures = []
    l_objs = listdir_fullpath( WORK_DIR + "/data/objects" )


    for path in l_objs:
        try:
            with open(path, "rb") as f:
                fixture = pickle.load(f)
            fixtures.append( fixture )
        except Exception as e:
            print("Error", str(e))

    if params:
        {
        'time': '2020-07-21:2020-07-22', 'name_market': '', 
        't1name': '', 't2name': '', 'sum_t1': '100', 'sum_t2': '100', 'num_snapshot': '5'}
        params['time'] = convert_date( params['time'] )
        params['sum_t1'] = int( params['sum_t1'] )
        params['sum_t2'] = int( params['sum_t2'] )
        params['num_snapshot'] = int( params['num_snapshot'] )
        query = get_search( params, fixtures )

        data['result'] = query
        data['params'] = params

    data["name_markets"] = name_markets_prepare( fixtures )

    data["name_markets"] = list( filter(lambda x: not re.search(pattern01, x), data["name_markets"] ) )
    data["teams"] = sorted( set( itertools.chain.from_iterable( [ [x.team01, x.team02] for x in fixtures] ) ) )

    return render_template("filter.html", data = data)



if __name__ == '__main__':

    if os.getenv("APP_PATH", False):
        serve(app, host='0.0.0.0', port=5000)
    else:
        app.run(port=5010, host='0.0.0.0', debug=True)
