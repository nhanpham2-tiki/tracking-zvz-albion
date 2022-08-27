from datetime import datetime
from typing import List
import openpyxl

class HandlerExcel():
    def __init__(self, filename):
        self.workbook = openpyxl.load_workbook(filename=filename, data_only=True)
        try:
            zvz_date = self.workbook.sheetnames[0].replace('ZvZ Attendance - ', '')
            self.date = datetime.strptime(zvz_date, '%Y-%m-%d')
        except Exception as err:
            raise err

    '''Rule:
    Default 1 worksheet with cols: Id, Name, Kills,	Deaths,	AVG IP,	Attendance,	Last Activity
    Every players with Attendance >= 1 is attending CTA
    Return list players who attend
    '''
    def parse_attendance(self) -> List[str]:
        worksheet = self.workbook.worksheets[0]
        attend_players = []

        # Read from line 2
        row = 2
        try:
            while True:
                player_info = worksheet[row]
                player_name = player_info[1]
                attend_time = player_info[5]
            
                if attend_time.value is None:
                    break
                if int(attend_time.value) > 0:
                    attend_players.append(player_name.value)
                row += 1
        except Exception as err:
            raise err

        return attend_players
