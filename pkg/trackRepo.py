import sqlite3
from datetime import date
from typing import List

from pkg.constant import SQLITE_DB


class TrackRepo():
    def __init__(self) -> None:
        self.conn = sqlite3.connect(SQLITE_DB)
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

    def UpdateAllPlayer(self, players: List[str]):
        insert_attend = """INSERT OR IGNORE INTO Player (NAME, ATTEND) Values ('{name}', {attend})"""
        cursor = self.conn.cursor()

        for player in players:
            cursor.execute(insert_attend.format(name=player, attend=0))
            self.conn.commit()

    def GetAllMatchTime(self) -> List[str]:
        result = []

        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT(ATTEND_DATE) from ATTEND')

        rows = cursor.fetchall()
        for row in rows:
            result.append(row[0])
        return result

    def GetAllPlayersName(self) -> List[str]:
        result = []

        cursor = self.conn.cursor()
        cursor.execute('SELECT NAME from PLAYER')

        rows = cursor.fetchall()
        for row in rows:
            result.append(row[0])
        return result

    def GetAllDateOfPlayer(self, name: str) -> List[str]:
        result = []

        cursor = self.conn.cursor()
        cursor.execute('''SELECT DISTINCT(ATTEND_DATE)
            from ATTEND
            where NAME = "{}"
            ORDER BY ATTEND_DATE DESC'''.format(name))

        rows = cursor.fetchall()
        for row in rows:
            result.append(row[0])
        return result

    def DeleteDate(self, date: date):
        delete_by_date = """DELETE FROM ATTEND WHERE ATTEND_DATE = '{date}'"""
        cursor = self.conn.cursor()
        cursor.execute(delete_by_date.format(date=date))
        self.conn.commit()

    def __update_players__(self, players: List[str]):
        select_attend = """SELECT ATTEND FROM Player Where NAME = '{}'"""
        update_attend = """UPDATE Player SET ATTEND = {attend} WHERE NAME = '{name}'"""
        cursor = self.conn.cursor()

        for player in players:
            cursor.execute(select_attend.format(player))
            record = cursor.fetchone()
            new_attend = record[0] + 1
            cursor.execute(update_attend.format(
                name=player, attend=new_attend))
            self.conn.commit()

    def __update_log__(self, players: List[str], date: date):
        check_exist = """SELECT EXISTS(
            SELECT * FROM Attend 
            WHERE NAME = '{name}'and ATTEND_DATE = '{attend_date}')"""
        insert_attend = """INSERT INTO Attend (NAME, ATTEND_DATE) Values ('{name}', '{attend_date}')"""
        cursor = self.conn.cursor()

        for player in players:
            # Remove duplicate chance
            cursor.execute(check_exist.format(name=player, attend_date=date))
            result = cursor.fetchone()
            if result[0] == 0:
                cursor.execute(insert_attend.format(name=player, attend_date=date))
                self.conn.commit()

    def clean(self):
        self.conn.execute("DROP TABLE Player")
        self.conn.execute("DROP TABLE Attend")
        self.conn.commit()
