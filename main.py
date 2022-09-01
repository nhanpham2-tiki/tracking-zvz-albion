# https://discord.com/api/oauth2/authorize?client_id=893693054899347467&permissions=27917544512&scope=bot

import os

import discord
from dotenv import load_dotenv

from pkg import discordClient

if __name__ == '__main__':
    load_dotenv()

    intents = discord.Intents.default()
    intents.message_content = True

    client = discordClient.DiscordClient(intents=intents)
    client.run(os.getenv('TOKEN'))
