import os
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from discord.ext import commands

from .base import BaseCog


class SpotifyCog(BaseCog):
    def __init__(self, client):
        super().__init__(client)
        load_dotenv()

        self.bot = client
        self.auth_manager = SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri='http://localhost:8000/callback',
            scope='user-read-playback-state,user-modify-playback-state'
        )

        self.spotify = Spotify(auth_manager=self.auth_manager)

    @commands.command('play')
    async def play(self, ctx, *, query):
        voice_client = None
        try:
            results = self.spotify.search(q=query, type='track', limit=5)
            message = "**Elige una canción:**\n"

            for i, track in enumerate(results['tracks']['items']):
                message += f"{i + 1}. {track['name']} - {track['artists'][0]['name']}\n"

            await ctx.send(message)

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.isdigit() and 1 <= int(
                    msg.content) <= 5

            response = await self.bot.wait_for('message', check=check, timeout=60.0)

            if response is None:
                await ctx.send("No se recibió respuesta a tiempo. Cancelando la operación.")
                return

            voice_client = await ctx.author.voice.channel.connect()

            if not voice_client.is_connected():
                await ctx.send("Failed to connect to voice channel.")
                return

            track_id = results['tracks']['items'][int(response.content) - 1]['id']
            await self.spotify.start_playback(uris=[f"spotify:track:{track_id}"], device_id=voice_client.guild.id)

            await ctx.send(f"Now playing: {results['tracks']['items'][int(response.content) - 1]['name']}")
        except Exception as e:
            print(f"Error playing Spotify audio: {e}")
            await ctx.send(f"An error occurred while playing Spotify audio.")
            if voice_client:
                await voice_client.disconnect()
