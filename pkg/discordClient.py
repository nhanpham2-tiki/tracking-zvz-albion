import os
from ast import arg
from typing import Any
from datetime import datetime

import discord

from pkg.aotoolParser import aoToolParser
from pkg.handlerExcel import HandlerExcel
from pkg.trackRepo import TrackRepo


class DiscordClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options: Any) -> None:
        super().__init__(intents=intents, **options)
        self.trackRepo = TrackRepo()

    async def bot_log(self, channel: discord.TextChannel, log: str):
        await channel.send(log)

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Chaos in GSW"))
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
            args = message.content.lower().split()
            if len(args) <= 1:
                await self.bot_log(message.channel, "Missing CTA time")
                return
            try:
                time = int(args[1])
                parser = aoToolParser(time)
                attend_players = parser.ParsePlayerAttend()

                current_date = datetime.utcnow().replace(hour=time, minute=0, second=0, microsecond=0)
                self.trackRepo.update_attend(
                    players=attend_players, date=current_date)

                await self.bot_log(message.channel, "Done !")
                
                # Log after match
                result_log = 'CTA Time: {}\n'.format(current_date.strftime('%Y-%m-%d %H:%M:%S'))
                result_log += ("-" * 30 + '\n')
                for player in attend_players:
                    result_log += (player + "\n")
                result_log += ("-" * 30 + '\n')
                result_log += ("Total attend: {}".format(len(attend_players)))
                await self.bot_log(message.channel, result_log)
            except Exception as err:
                await self.bot_log(message.channel, "Error while parse data: {}".format(err))
                return

        # ! Report detail as excel
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

            if message.content.lower().startswith('!reverse'):
                pass

            # !add player_name date(yyyy-mm-dd) time(hh)
            if message.content.lower().startswith('!add'):
                args = message.content.split()
                if len(args) != 4:
                    await self.bot_log(message.channel, "Wrong format: !add name yyyy-mm-dd hour")
                    return

                date, hour = None, None
                try:
                    date = datetime.strptime(args[2], '%Y-%m-%d')
                    hour = int(args[3])
                except:
                    await self.bot_log(message.channel, "Wrong format: !add name yyyy-mm-dd hour")
                    return

                current_date = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                attend_players = [args[1]]
                self.trackRepo.update_attend(
                    players=attend_players, date=current_date)

                await self.bot_log(message.channel, "Done !")

            # if message.content.lower().startswith('!manual'):
            #     if len(message.attachments) == 0:
            #         await self.bot_log(message.channel, "Missing Excel Tracking file")
            #         return

            #     attachment_name = message.attachments[0].filename
            #     await message.attachments[0].save(attachment_name)

            #     try:
            #         handlerExcel = HandlerExcel(attachment_name)
            #         attend_players = handlerExcel.parse_attendance()
            #         attend_date = handlerExcel.date

            #         self.trackRepo.update_attend(
            #             players=attend_players, date=attend_date)
            #     except Exception as err:
            #         await self.bot_log(message.channel, err)

            #     os.remove(attachment_name)
            #     await self.bot_log(message.channel, "Done !")
            #     return
