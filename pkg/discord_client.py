import os
from typing import Any
import discord

from pkg.trackRepo import TrackRepo
from pkg.handlerExcel import HandlerExcel


class DiscordClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options: Any) -> None:
        super().__init__(intents=intents, **options)
        self.trackRepo = TrackRepo()

    async def bot_log(self, channel: discord.TextChannel, log: str):
        await channel.send(log)

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    def isDev(self, message):
        for i in range(1, int(os.getenv('DEV_COUNT')) + 1):
            if str(message.author) == os.getenv('AUTHOR_{}'.format(i)):
                return True
        else:
            return False

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.lower().startswith('!ping'):
            await message.channel.send('Bot is running!')
            return

        if message.content.lower().startswith('!checkin'):
            if len(message.attachments) == 0:
                await self.bot_log(message.channel, "Missing Excel Tracking file")
                return

            attachment_name = message.attachments[0].filename
            await message.attachments[0].save(attachment_name)

            try:
                handlerExcel = HandlerExcel(attachment_name)
                attend_players = handlerExcel.parse_attendance()
                attend_date = handlerExcel.date

                self.trackRepo.update_attend(
                    players=attend_players, date=attend_date)
            except Exception as err:
                await self.bot_log(message.channel, err)

            os.remove(attachment_name)
            await self.bot_log(message.channel, "Done !")
            return

        if message.content.lower().startswith('!report'):
            player_attend = self.trackRepo.report_player()
            result = '{:<15} {:>8}\n'.format('Name', "Attend")
            for player_name, attend in player_attend.items():
                result += "{:<20} {:>3}\n".format(player_name, attend)
            
            result += 'Total CTA: {}'.format(self.trackRepo.total_matches())

            await self.bot_log(message.channel, result)
            return

        if self.isDev(message):
            if message.content.lower().startswith('!clear'):
                self.trackRepo.clean()
                self.trackRepo.initDB()
                await self.bot_log(message.channel, "Done !")
                return 
