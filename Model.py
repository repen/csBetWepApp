from peewee import *
from Globals import WORK_DIR
from datetime import datetime
# from data_prepare import data_filter, Match, MatchMovedError

db = SqliteDatabase(WORK_DIR + "/data/database/csgo.db")


class CSGame(Model):
    m_id     = CharField()
    m_time   = IntegerField()
    team1    = CharField()
    team2    = CharField()

    class Meta:
        database = db

class Market:
    def __init__(self, *args):
        self.name  = args[0]
        self.left  = args[1]
        self.right = args[2]
        self.winner = args[3]
        self.time_snapshot = args[4]

class Fixture:
    def __init__(self,*args):
        self.qid    = args[0]
        self.m_id   = args[1]
        self.m_time = args[2]
        self.team01 = args[3]
        self.team02 = args[4]
        self._name_markets = set()
        # self._markets = []
        self._snapshots = []

    @property
    def markets(self):
        return self._snapshots

    @markets.setter
    def markets(self, elements):
        self._snapshots.append( elements )

    @markets.getter
    def markets(self):
        return self._snapshots

    @property
    def name_markets(self):
        return self._name_markets

    @name_markets.setter
    def name_markets(self, names):
        for name in names:
            self._name_markets.add( name )

    @name_markets.getter
    def name_markets(self,):
        return self._name_markets

if __name__ == '__main__':
    pass
