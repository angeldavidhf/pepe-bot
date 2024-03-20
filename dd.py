import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp as youtube_dl

load_dotenv()

intents = discord.Intents.all()
intents.voice_states = True

bot = commands.Bot(command_prefix=os.getenv('PREFIX'), intents=intents, ffmpeg="/opt/homebrew/bin/ffmpeg")



if not discord.opus.is_loaded():
    discord.opus.load_opus("opus.dll")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="Barking!", url="https://twitch.tv/agua_paneia"))
    print("on duty!")


@bot.command(name="ping")
async def ping(ctx):
    channel = bot.get_channel(1219405820698169476)
    await channel.send('pong')


@bot.command(name="join")
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect(self_deaf=True)
    else:
        await ctx.send("You must be on a voice channel for me to join!")


@bot.command(name="leave")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("What are you saying bobolón, I'm not on any channel!")


@bot.command(name="play")
async def play(ctx, song_url: str):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect(self_deaf=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_url, download=False)
            url = info['url']

        ffmpeg_audio = discord.FFmpegPCMAudio(url)
        voice_client.play(ffmpeg_audio)
        await ctx.send(f'Playing popochas')
    else:
        await ctx.send("You must be on a voice channel for me to join!")


bot.run(os.getenv('DISCORD_TOKEN'))
