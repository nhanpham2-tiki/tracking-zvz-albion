from datetime import date
import sqlite3
import string
from turtle import st
from typing import List
from unicodedata import name


class TrackRepo():
    def __init__(self) -> None:
        self.conn = sqlite3.connect('sql/track.db')
        self.initDB()

    def initDB(self):
        # Create player record
        self.conn.execute('''CREATE TABLE IF NOT EXISTS Player
            (NAME    TEXT PRIMARY KEY  NOT NULL,
            ATTEND  INT     NOT NULL);''')
        # Create attend log
        self.conn.execute('''CREATE TABLE IF NOT EXISTS Attend
            (ID             INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME            TEXT    NOT NULL,
            ATTEND_DATE     TEXT    NOT NULL)''')
        self.conn.commit()

    '''
    date format: '%Y-%m-%d' or '%Y-%m-%d %H:%M%S'
    '''
    def update_attend(self, players: List[str], date: date):
        self.__update_players__(players)
        self.__update_log__(players, date)

    def report_player(self) -> dict:
        player_attend = dict()

        cursor = self.conn.cursor()
        cursor.execute("""SELECT * FROM Player""")
        rows = cursor.fetchall()
        for row in rows:
            player_attend[row[0]] = row[1]
        return player_attend

    def total_matches(self):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT COUNT( DISTINCT ATTEND_DATE ) 
            AS "Number of CTA" 
            FROM Attend;""")
        record = cursor.fetchone()[0]
        return record

    def __update_players__(self, players: List[str]):
        select_attend = """SELECT ATTEND FROM Player Where NAME = '{}'"""
        insert_attend = """INSERT OR IGNORE INTO Player (NAME, ATTEND) Values ('{name}', {attend})"""
        update_attend = """UPDATE Player SET ATTEND = {attend} WHERE NAME = '{name}'"""
        cursor = self.conn.cursor()

        for player in players:
            cursor.execute(select_attend.format(player))
            record = cursor.fetchone()
            new_attend = 0
            if record is None:
                new_attend = 1
            else:
                new_attend = record[0] + 1
            cursor.execute(insert_attend.format(
                name=player, attend=new_attend))
            cursor.execute(update_attend.format(
                name=player, attend=new_attend))
            self.conn.commit()

    def __update_log__(self, players: List[str], date: date):
        insert_attend = """INSERT INTO Attend (NAME, ATTEND_DATE) Values ('{name}', '{attend_date}')"""
        cursor = self.conn.cursor()

        for player in players:
            cursor.execute(insert_attend.format(name=player, attend_date=date))
            self.conn.commit()

    def clean(self):
        self.conn.execute("DROP TABLE Player")
        self.conn.execute("DROP TABLE Attend")
        self.conn.commit()
