import ast
from typing import List

import requests
from bs4 import BeautifulSoup

from pkg.constant import ZVZ_API


class aoToolParser():
    def __init__(self, CTA_time: int) -> None:
        self.CTA_time = CTA_time
        if self.CTA_time >= 10:
            self.min_players = 15
        else:
            self.min_players = 10

    def ParsePlayerAttend(self) -> List[str]:
        response = requests.get(ZVZ_API.format(
            player=self.min_players, start=self.CTA_time-1, end=self.CTA_time))

        soup = BeautifulSoup(response.content, 'html.parser')
        div_players = soup.find('div', id='download').string
        players = ast.literal_eval(div_players)

        self.attend_player = []
        for playerInfo in players:
            if playerInfo[5] >= '1':
                self.attend_player.append(playerInfo[1])
        return self.attend_player
