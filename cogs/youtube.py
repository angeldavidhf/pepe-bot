import os
import discord
import asyncio
import yt_dlp
from dotenv import load_dotenv


def run_bot():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.all()
    intents.message_content = True
    client = discord.Client(intents=intents)

    queue = {}
    voice_clients = {}
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }
    ffmpeg_opts = {
        'options': '-vn'
    }

    ytdl = yt_dlp.YoutubeDL(ydl_opts)

    @client.event
    async def on_ready():
        await client.change_presence(activity=discord.Streaming(name="Barking!", url="https://twitch.tv/agua_paneia"))
        print(f"{client.user} on duty!")

    @client.event
    async def on_message(message):
        if message.content.startswith(';;play'):
            try:
                voice_client = await message.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client

                url = message.content.split()[1]

                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

                song = data['url']
                player = discord.FFmpegPCMAudio(song, **ffmpeg_opts)

                voice_clients[message.guild.id].play(player)
                # voice_client.play(player)
            except Exception as e:
                print(e)

        if message.content.startswith(';;pause'):
            try:
                voice_clients[message.guild.id].pause()
            except Exception as e:
                print(e)

        if message.content.startswith(';;resume'):
            try:
                voice_clients[message.guild.id].resume()
            except Exception as e:
                print(e)

        if message.content.startswith(';;stop'):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
            except Exception as e:
                print(e)

        if message.content.startswith(';;queue'):
            try:
                pass
            except Exception as e:
                print(e)

    client.run(TOKEN)
