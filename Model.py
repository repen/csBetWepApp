from peewee import *
from Globals import DB_DIR
from datetime import datetime

db = SqliteDatabase(DB_DIR + "/csgo.db")


class CSGame(Model):
    m_id     = CharField()
    m_time   = IntegerField()
    snapshot = BlobField()
    active   = IntegerField()

    class Meta:
        database = db



if __name__ == '__main__':
    pass
