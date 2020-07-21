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



if __name__ == '__main__':
    pass
