import asyncio

import yt_dlp
import discord
from discord.ext import commands
from .base import BaseCog


class YouTubeCog(BaseCog):
    def __init__(self, client):
        super().__init__(client)
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }
        self.ffmpeg_options = {
            'options': '-vn -nostdin'
        }
        self.ytdl = yt_dlp.YoutubeDL(self.ydl_opts)
        self.voice_clients = {}

    @commands.command(name="play")
    async def play(self, ctx, url):
        voice_client = None
        try:
            voice_client = await ctx.author.voice.channel.connect()
            self.voice_clients[ctx.guild.id] = voice_client

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, **self.ffmpeg_options)

            voice_client.play(player)
            await ctx.send(f"Playing {data['title']}")
        except Exception as e:
            print(f"Error playing YouTube audio: {e}")
            await ctx.send(f"An error occurred while playing YouTube audio")

            if voice_client:
                await voice_client.disconnect()
                del self.voice_clients[ctx.guild.id]


