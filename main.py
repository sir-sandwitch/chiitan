import re
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import atexit


vc = None

song_ids = {}

current_queue_location = None

def update_song_ids(d):
    if d['status'] == 'finished':
        video_id = d['info_dict']['id']
        title = d['info_dict']['title']
        song_ids[video_id] = title
    
downloader = YoutubeDL({
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': './Songs/%(id)s.%(ext)s',
    'quiet': True,
    'progress_hooks': [update_song_ids]
})

started = False

queue = []

SPOTIFY_SONG = 1
YOUTUBE_SONG = 2

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="chiitan my one and only love in this world pretty please will you ", intents=intents)

# Spotify API setup
SPOTIFY_CLIENT_ID = open('spotify_id.txt').read()
SPOTIFY_CLIENT_SECRET = open('spotify_secret.txt').read()
SPOTIFY_REDIRECT_URI = 'https://google.com/callback'

scope = "user-read-playback-state user-modify-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope=scope))



# def is_supported(url):
#     extractors = youtube_dl.extractor.gen_extractors()
#     for e in extractors:
#         if e.suitable(url) and e.IE_NAME != 'generic':
#             return True
#     return False

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def join(ctx):
    global vc
    if ctx.author.voice and (vc == None or not vc.is_connected()):
        vc = await ctx.message.author.voice.channel.connect()
    elif (vc != None and vc.is_connected()):
        await vc.move_to(ctx.message.author.voice.channel)
    else:
        await ctx.send("ermmmmmmm, Chii-tan can't find youuuuuuuu (ಡ‸ಡ)")
        return

       
    await ctx.send("Chii-tan has entered your home! ♡＼(￣▽￣)／♡")

@bot.command()
async def pause(ctx):
    if vc.is_playing():
        vc.pause()
        await ctx.send("Chii-tan has paused the music! (´｡• ᵕ •｡`) ♡")
    else:
        await ctx.send("Chii-tan isn't playing anything right now, so she can't pause it... (ಡ‸ಡ)")

@bot.command()
async def resume(ctx):
    if vc.is_paused():
        vc.resume()
        await ctx.send("Chii-tan has resumed the music! (´｡• ᵕ •｡`) ♡")
    else:
        await ctx.send("Chii-tan isn't paused right now, so she can't resume it... (ಡ‸ಡ)")

remove_from_array = lambda arr, index: arr[:index] + arr[index + 1:]

@bot.command()
async def skip(ctx):
    global current_queue_location
    if vc.is_playing():
        vc.stop()
        if current_queue_location != None:
            queue = remove_from_array(queue, current_queue_location)
        await start(ctx)
        await ctx.send("Chii-tan has skipped the song and removed! (´｡• ᵕ •｡`) ♡")
    else:
        await ctx.send("Chii-tan isn't playing anything right now, so she can't skip it... (ಡ‸ಡ)")

async def play_next(ctx):
    global current_queue_location
    if len(queue) < 1:
        return
    if current_queue_location == None:
        current_queue_location = 0
    if current_queue_location + 1 < len(queue):
        song_id = queue[current_queue_location + 1].split('/')[-1].split('.')[0]
        await ctx.send(f"Chii-tan is now playing {song_ids[song_id]}! (* ^ ω ^)")
        vc.play(discord.FFmpegOpusAudio(queue[current_queue_location + 1]), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        current_queue_location += 1
    else:
        current_queue_location = 0
        song_id = queue[current_queue_location].split('/')[-1].split('.')[0]
        await ctx.send(f"Chii-tan is now playing {song_ids[song_id]}! (* ^ ω ^)")
        vc.play(discord.FFmpegOpusAudio(queue[current_queue_location]), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        
async def start(ctx):
    global vc
    if vc is None or not vc.is_connected():
        await ctx.send("Chii-tan isn't in a vc right now, so she can't play anything for youuuuuuuu (ಡ‸ಡ)")
        return

    if len(queue) == 0:
        await ctx.send("Chii-tan doesn't have any songs to play for youuuuuuuu (ಡ‸ಡ)")
        return

    if not vc.is_playing():
        await play_next(ctx)

@bot.command()
async def die(ctx):
    global vc
    if ctx.author.voice and (vc != None and vc.is_connected()):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("okay fineeeeeee,,,,,,,, Chii-tan will die... (╥﹏╥)")
    else:
        await ctx.send("uhm, one of us isn't in a vc and Chii-tan thinks she knows who it is... (⁄ ⁄•⁄ω⁄•⁄ ⁄)")

@bot.command()
async def sing(ctx, url):
    global vc
    if vc == None or not vc.is_connected():
        await ctx.send("Chii-tan isn't in a vc right now, so she can't play anything for youuuuuuuu (ಡ‸ಡ)")
        return
    
    spotify_url_pattern = r'(https?://open\.spotify\.com/track/([a-zA-Z0-9]+)\??.*)'
    
    youtube_playlist = re.match(r"https://www.youtube.com/playlist\?list=.*", url)
    spotify_playlist = re.match(r"https://open.spotify.com/playlist/.*", url)
    spotify_album = re.match(r"https://open.spotify.com/album/.*", url)
    spotify_url = re.match(spotify_url_pattern, url)
    youtube_url = re.match(r"https://www.youtube.com/watch\?v=.*", url)

    downloader_new = None

    async def download_song(url, folder_name):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, downloader.download, [url])
        video_id = url.split('=')[-1]
        return f'{folder_name}/{video_id}.mp3'

    if youtube_url:
        await ctx.send("Chii-tan is fetching your song! (ﾉ´ з `)ノ")
        song_path = await download_song(url, './Songs')
        queue.append(song_path)
        await ctx.send("Chii-tan has finished downloading your song! ( ´ ∀ `)ノ～ ♡")

    elif spotify_url:
        track_uri = f'spotify:track:{spotify_url.group(2)}'
        track_info = sp.track(track_uri)
        if track_info:
            search = track_info['name'] + ' ' + track_info['artists'][0]['name']
            await ctx.send("Chii-tan is fetching your song! (ﾉ´ з `)ノ")
            info = downloader.extract_info(f'ytsearch:{search}', download=False)
            video_id = info['entries'][0]['id']
            song_path = await download_song(f'https://www.youtube.com/watch?v={video_id}', './Songs')
            queue.append(song_path)
            await ctx.send("Chii-tan has finished downloading your song! ( ´ ∀ `)ノ～ ♡")
        else:
            await ctx.send("Chii-tan couldn't find your song... (ಡ‸ಡ)")
            return

    elif youtube_playlist or spotify_playlist or spotify_album:
        await ctx.send("Chii-tan is fetching your playlist/album! (ﾉ´ з `)ノ")
        loop = asyncio.get_event_loop()

        folder_name = './Songs/'
        
        if youtube_playlist:
            id = url.split('=')[-1]
            is_playlist = True
        
        elif spotify_playlist or spotify_album:
            id = url.split('/')[-1].split('?')[0] if '?' in url else url.split('/')[-1]
            is_playlist = True

        if youtube_playlist:
            await loop.run_in_executor(None, downloader_new.download, [url])
            first_song = os.listdir(folder_name)[0]
            queue.append(f'{folder_name}/{first_song}')
            if not vc.is_playing():
                await start(ctx)
            for file in os.listdir(folder_name)[1:]:
                queue.append(f'{folder_name}/{file}')
        elif spotify_playlist or spotify_album:
            if spotify_playlist:
                playlist_info = sp.playlist(id)
                tracks = playlist_info['tracks']['items']
            elif spotify_album:
                album_info = sp.album(id)
                tracks = album_info['tracks']['items']
            first_track = tracks[0]
            track_uri = first_track['track']['uri'] if spotify_playlist else first_track['uri']
            track_info = sp.track(track_uri)
            search = track_info['name'] + ' ' + track_info['artists'][0]['name']
            info = downloader.extract_info(f'ytsearch:{search}', download=False)
            video_id = info['entries'][0]['id']
            first_song_path = await download_song(f'https://www.youtube.com/watch?v={video_id}', folder_name)
            queue.append(first_song_path)
            if not vc.is_playing():
                await start(ctx)
            for track in tracks[1:]:
                track_uri = track['track']['uri'] if spotify_playlist else track['uri']
                track_info = sp.track(track_uri)
                search = track_info['name'] + ' ' + track_info['artists'][0]['name']
                info = downloader.extract_info(f'ytsearch:{search}', download=False)
                video_id = info['entries'][0]['id']
                song_path = await download_song(f'https://www.youtube.com/watch?v={video_id}', folder_name)
                queue.append(song_path)

    else:
        await ctx.send("Chii-tan doesn't know how to play that song for youuuuuuuu (ಡ‸ಡ)")
        return
    
    if not vc.is_playing():
        await start(ctx)

@bot.command()
async def list(ctx):
    if len(queue) == 0:
        await ctx.send("Chii-tan doesn't have any songs to play for youuuuuuuu (ಡ‸ಡ)")
        return

    song_list = ""
    for i, song in enumerate(queue):
        song_id = song.split('/')[-1].split('.')[0]
        song_list += f"{i + 1}. {song_ids[song_id]}\n"

    await ctx.send(f"Chii-tan has the following songs in the queue:\n{song_list}")

@bot.command()
async def shut(ctx, arg):
    global queue
    if arg == "up":
        # clear the queue
        queue = []
        await skip(ctx)
        await ctx.send("Chii-tan has cleared the queue! (´｡• ᵕ •｡`) ♡")

        # delete all the songs
        for file in os.listdir('./Songs'):
            os.remove(f'./Songs/{file}')

bot.remove_command('help')

@bot.command()
async def help(ctx):
    await ctx.send("Chii-tan is here to help youuuuuuuu! (ﾉ´ з `)ノ\n\n"
                     "Here are the commands you can use:\n"
                        "1. `join` - Chii-tan will join your voice channel\n"
                        "2. `sing <url>` - Chii-tan will play the song from the url\n"
                        "3. `pause` - Chii-tan will pause the music\n"
                        "4. `resume` - Chii-tan will resume the music\n"
                        "5. `skip` - Chii-tan will skip the current song\n"
                        "6. `list` - Chii-tan will list the songs in the queue\n"
                        "7. `shut up` - Chii-tan will clear the queue\n"
                        "8. `die` - Chii-tan will leave the voice channel\n"
                        "9. `help` - Chii-tan will show you this message again\n")

def exit_handler():
    if vc != None and vc.is_connected():
        vc.disconnect()
        
    # delete all the songs
    for file in os.listdir('./Songs'):
        os.remove(f'./Songs/{file}')

def main():

    #authenticate spotify
    sp.current_user_playing_track()

    atexit.register(exit_handler)

    try:
        with open('./token.txt') as t:
            bot.run(t.read())
    except KeyboardInterrupt:
        exit_handler()

        


if __name__ == "__main__":
    main()