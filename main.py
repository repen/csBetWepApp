from flask import Flask, render_template, request
import os, json, re
from Model import CSGame
from parser_data import hand_snapshot
from bs4 import BeautifulSoup
from datetime import datetime
from Globals import WORK_DIR

app = Flask(__name__)


def link_matches(s_time):
    '''Generate list id_matches'''
    c = 0

    def load_team(snapshots):
        if snapshots:
            if len(snapshots) > 1:
                html = snapshots[-2]["data"]
            else:
                html = snapshots[-1]["data"]


            soup = BeautifulSoup(html, "html.parser")
            team1_name = soup.select_one(".bet-team__name.sys-t1name").text.strip() if soup.select_one(".bet-team__name.sys-t1name") else "0"
            team2_name = soup.select_one(".bet-team__name.sys-t2name").text.strip() if soup.select_one(".bet-team__name.sys-t2name") else "0"
        
            result_String = re.sub(r"^\d+\s|\d+\s?$", "", team1_name + " vs " + team2_name)
            return result_String.replace("null", "")
        return 'init' + " vs " + "init"

    def init_cache_m_id():

        def init_cache():
            dict_data = {}
            try:
                with open(WORK_DIR +'/m_names.txt') as f:
                    data = f.read()
                dict_data = {
                    row.split(":")[0]:row.split(":")[1]
                    for row in data.strip().split("\n")
                }
            except IOError:
                pass
            return dict_data
        cache = init_cache()
        def load_name_match(*args):
            m_id = args[0]
            obj_db = args[1]
            if m_id in cache.keys():
                return cache[m_id]
            else:
                result = load_team( json.loads(obj_db.__data__['snapshot']))
                if "init vs" not in result and "TBD" not in result:
                    with open(WORK_DIR + "/m_names.txt", 'a', encoding="utf8") as f:
                        f.write("{}:{}\n".format(m_id, result))
                return result
        return load_name_match

    fixtures = CSGame.select().where( (s_time < CSGame.m_time) & (CSGame.m_time < s_time + 87000))
    cache_m_id = init_cache_m_id()
    data = [
        [
            x.__data__['m_id'],
            cache_m_id(x.__data__['m_id'], x),
            datetime.fromtimestamp(int(x.__data__['m_time'])).strftime("%Y.%m.%d %H:%M")
        ] for x in fixtures
    ]
    return data

def content(m_id):
    fixtures = CSGame.select().where(CSGame.m_id == m_id)

    for fixture in fixtures:
        snapshot = json.loads(fixture.__data__['snapshot'])
        accum = []
        for snap in snapshot:
            result = hand_snapshot(snap['data'])
            accum.append(result)
        return " ".join(accum)


@app.route('/')
def index():
    select_time = datetime.now().timestamp()
    date = request.args.get('date', default=False)

    if date:
        select_time = datetime.strptime(date, "%m/%d/%Y").timestamp()
    data = {"links" : link_matches(select_time)}
    return render_template("index.html", data = data)

@app.route('/match/<m_id>')
def match_page(m_id):
    data = {"content" : content(m_id)}
    return render_template("match.html", data = data)


if __name__ == '__main__':
    if os.getenv("APP_PATH", False):
        app.run()
    else:
        app.run(port=5010, host='0.0.0.0', debug=True)
