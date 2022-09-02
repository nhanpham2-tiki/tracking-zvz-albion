import os
from datetime import datetime
from typing import Any

import discord

from pkg.aotoolParser import aoToolParser
from pkg.constant import CLONE_TXT, SQLITE_DB
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

        self.clone = []
        with open(CLONE_TXT, 'r') as clone_file:
            while True:
                clone = clone_file.readline()
                if not clone:
                    break
                self.clone.append(clone.replace('\n', ''))

    def isDev(self, message):
        for i in range(1, int(os.getenv('DEV_COUNT')) + 1):
            if str(message.author.id) == os.getenv('AUTHOR_{}'.format(i)):
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
                all_players = parser.ParseAllPlayer()
                self.trackRepo.UpdateAllPlayer(players=all_players)

                attend_players = parser.ParsePlayerAttend()
                # Corner case: log at 2/9/2022 3utc for 1/9/2022 15utc
                # Wrong input date: 2/9/2022 15utc
                if datetime.utcnow().hour < time:
                    current_date = datetime.utcnow()
                    current_date = current_date.replace(
                        day=current_date.day - 1, hour=time, minute=0, second=0, microsecond=0)
                else:
                    current_date = datetime.utcnow().replace(
                        hour=time, minute=0, second=0, microsecond=0)

                self.trackRepo.update_attend(
                    players=attend_players, date=current_date)

                await self.bot_log(message.channel, "Done !")

                # Log after match
                result_log = 'CTA Time: {}\n'.format(
                    current_date.strftime('%Y-%m-%d %H:%M:%S'))
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
            excelExport = HandlerExcel()
            excelExport.ExportData(trackRepo=self.trackRepo, clone_list=self.clone)

            file = discord.File(excelExport.fileName)
            await message.channel.send(file=file, content="GSW Tracking")
            return

        if self.isDev(message):
            if message.content.startswith('!clear_tracking'):
                self.trackRepo.clean()
                self.trackRepo.initDB()
                await self.bot_log(message.channel, "Done !")
                return

            # !reverse date(yyyy-mm-dd) time(hh)
            if message.content.lower().startswith('!reverse'):
                args = message.content.split()
                if len(args) != 3:
                    await self.bot_log(message.channel, "Wrong format: !reverse yyyy-mm-dd hour")
                    return

                date, hour = None, None
                try:
                    date = datetime.strptime(args[1], '%Y-%m-%d')
                    hour = int(args[2])
                except:
                    await self.bot_log(message.channel, "Wrong format: !reverse yyyy-mm-dd hour")
                    return

                current_date = date.replace(
                    hour=hour, minute=0, second=0, microsecond=0)

                self.trackRepo.DeleteDate(date=current_date)
                await self.bot_log(message.channel, "Done !")

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

                current_date = date.replace(
                    hour=hour, minute=0, second=0, microsecond=0)
                attend_players = [args[1]]
                self.trackRepo.update_attend(
                    players=attend_players, date=current_date)

                await self.bot_log(message.channel, "Done !")

            # * Export SQLite file
            if message.content.lower().startswith('!export'):
                file = discord.File(SQLITE_DB)
                await message.channel.send(file=file)
                return

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
