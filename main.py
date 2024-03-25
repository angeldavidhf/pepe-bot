import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from cogs.youtube import YouTubeCog
# from cogs.spotify import SpotifyCog


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="?", intents=discord.Intents.all())
        load_dotenv()

    async def on_ready(self):
        await self.change_presence(activity=discord.Streaming(name="Barking!", url="https://twitch.tv/agua_paneia"))
        print(f"{self.user} on duty!!")


if __name__ == "__main__":
    discord.opus.load_opus("/opt/homebrew/Cellar/opus/1.5.1/lib/libopus.dylib")
    bot = Bot()

    async def add_cogs():
        await bot.add_cog(YouTubeCog(bot))
        # await bot.add_cog(SpotifyCog(bot))
    asyncio.run(add_cogs())
    bot.run(os.getenv("DISCORD_TOKEN"))
