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
            'options': '-vn',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        }
        self.ytdl = yt_dlp.YoutubeDL(self.ydl_opts)
        self.queue = []
        self.songs = []

    @commands.command(name="play")
    async def play(self, ctx, url):
        voice_client = ctx.guild.voice_client
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, **self.ffmpeg_options)

            if voice_client is None or not voice_client.is_connected():
                voice_client = await ctx.author.voice.channel.connect()

            if not self.queue:
                self.queue.append(player)
                self.songs.append(data['title'])
                await ctx.send(f"Now playing **{data['title']}**")

                voice_client.play(player)
            else:
                self.queue.append(player)
                self.songs.append(data['title'])
                await ctx.send(f"Added **{data['title']}** to the queue")
        except Exception as e:
            print(f"Error playing YouTube audio: {e}")
            await ctx.send(f"An error occurred while playing YouTube audio")

            if voice_client:
                await voice_client.disconnect()

    @commands.command(name="queue")
    async def queue(self, ctx):
        if not self.queue:
            await ctx.send("The queue is currently empty.")
            return

        message = "**Current queue:**\n"
        for i, name in enumerate(self.songs):
            message += f"{i+1}. {name}\n"

        await ctx.send(message)

    @commands.command(name="skip")
    async def skip(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("I'm not currently connected to a voice channel!")
            return
        if not self.queue:
            await ctx.send("There are no songs in the queue to skip!")
            return

        voice_client.stop()
        await ctx.send(f"Skipped **{self.songs[0]}** and playing the next song in the queue.")
        self.queue.pop(0)
        self.songs.pop(0)

        if self.queue:
            voice_client.play(self.queue[0])
            await ctx.send(f"Now playing **{self.songs[0]}**")

    @commands.command(name="pause")
    async def pause(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client is None or not voice_client.is_playing():
            await ctx.send("There is no music currently playing.")
            return

        voice_client.pause()
        await ctx.send(f"Paused **{self.songs[0]}**")

    @commands.command(name="resume")
    async def resume(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client is None or not voice_client.is_paused():
            await ctx.send("There is no paused music to resume.")
            return

        voice_client.resume()
        await ctx.send(f"Resume **{self.songs[0]}**")

    @commands.command(name="stop")
    async def stop(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("I am not connected to a voice channel.")
            return

        voice_client.stop()
        await ctx.send("Music stopped and disconnected from the voice channel.")
        await voice_client.disconnect()


