import discord
from discord.ext import commands


class BaseCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.client.user} on duty!")
