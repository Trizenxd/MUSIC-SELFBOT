import discord
from discord.ext import commands
import os
import colorama
from colorama import Fore
import wavelink
import platform
import psutil
import datetime

intents = discord.Intents.default()
intents.messages = True  

client = commands.Bot(command_prefix=[""], intents=intents, self_bot=True)
colorama.init(autoreset=True)

loop_status = {}

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='info')
    async def info(self, ctx):
        uptime = datetime.datetime.utcnow() - self.bot.uptime
        python_version = platform.python_version()
        discord_version = discord.__version__
        memory_usage = psutil.Process().memory_info().rss / 1024**2
        cpu_usage = psutil.cpu_percent()

        info_text = (
            f"```ini\n[ Bot Information ]\n```\n"
            f"```yaml\n"
            f"Bot Uptime: {uptime}\n"
            f"Python Version: {python_version}\n"
            f"Discord.py Version: {discord_version}\n"
            f"Memory Usage: {memory_usage:.2f} MB\n"
            f"CPU Usage: {cpu_usage:.2f}%\n"
            f"```\n"
            f"```ini\n[ Additional Info ]\n```\n"
            f"Owner: <@{self.bot.owner_id}>\n"
            f"Guilds: {len(self.bot.guilds)}\n"
            f"Users: {len(self.bot.users)}\n"
            f"Requested by: {ctx.author}\n"
        )

        await ctx.send(info_text)

async def setup(bot):
    bot.uptime = datetime.datetime.utcnow()
    await bot.add_cog(Info(bot))

@client.command(name='play')
async def play(ctx, *, query: str):
    if not ctx.author.voice:
        return await ctx.send("• *You need to be in a voice channel to play music.*")

    if not wavelink.NodePool.get_node():
        return await ctx.send("• *No nodes are connected. Please try again later.*")

    vc: wavelink.Player = ctx.voice_client
    if not vc:
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

    try:
        tracks = await wavelink.YouTubeTrack.search(query)
        if not tracks:
            return await ctx.send("• *No results found.*")

        track = tracks[0]
        await vc.play(track)
        await ctx.send(f"• *Now playing {track.title}*")
    except Exception as e:
        await ctx.send(f"• *Error: {e}*")
        if ctx.guild is None:
            return await ctx.send("• *This command can't be used in DMs.*")

@client.command(name='pause')
async def pause(ctx):
    vc: wavelink.Player = ctx.voice_client
    if ctx.guild is None:
        return await ctx.send("• *This command can't be used in DMs.*")

    if not vc:
        return await ctx.send("• *I'm not connected to a voice channel.*")

    if vc.is_playing():
        await vc.pause()
        await ctx.send("• *Paused the music.*")
    else:
        await ctx.send("• *There's nothing playing to pause.*")

@client.command(name='resume')
async def resume(ctx):
    vc: wavelink.Player = ctx.voice_client
    if ctx.guild is None:
        return await ctx.send("• *This command can't be used in DMs.*")

    if not vc:
        return await ctx.send("• *I'm not connected to a voice channel.*")
    
    if vc.is_paused():
        await vc.resume()
        await ctx.send("• *Resumed the music.*")
    else:
        await ctx.send("• *There's nothing paused to resume.*")

@client.command(name='stop')
async def stop(ctx):
    vc: wavelink.Player = ctx.voice_client
    if ctx.guild is None:
        return await ctx.send("• *This command can't be used in DMs.*")

    if not vc:
        return await ctx.send("• *I'm not connected to a voice channel.*")

    if vc.is_playing():
        await vc.stop()
        await ctx.send("• *Stopped the music.*")
    else:
        await ctx.send("• *There's nothing playing to stop.*")

    await vc.disconnect()

@client.command(name='volume', aliases=['vol'])
async def volume(ctx, level: int):
    if not 0 <= level <= 4000:
        return await ctx.send("• *Volume level must be between 0 and 4000.*")
    
    vc: wavelink.Player = ctx.voice_client
    if ctx.guild is None:
        return await ctx.send("• *This command can't be used in DMs.*")

    if not vc:
        return await ctx.send("• *I'm not connected to a voice channel.*")

    await vc.set_volume(level)
    await ctx.send(f"• *Volume set to {level}%*")

@client.command(name='volget')
async def vol_get(ctx):
    vc: wavelink.Player = ctx.voice_client
    if ctx.guild is None:
        return await ctx.send("• *This command can't be used in DMs.*")

    if not vc:
        return await ctx.send("• *I'm not connected to a voice channel.*")

    volume = vc.volume
    await ctx.send(f"• *Current volume is {volume}%*")

@client.command(name='seek')
async def seek(ctx, position: int):
    vc: wavelink.Player = ctx.voice_client
    if ctx.guild is None:
        return await ctx.send("• *This command can't be used in DMs.*")

    if not vc:
        return await ctx.send("• *I'm not connected to a voice channel.*")

    if vc.is_playing():
        await vc.seek(position * 1000)  
        await ctx.send(f"• *Seeked the song to {position} seconds.*")
    else:
        await ctx.send("• *There's no music playing to seek.*")

@client.command(name='loop')
async def loop(ctx):
    vc: wavelink.Player = ctx.voice_client
    if ctx.guild is None:
        return await ctx.send("• *This command can't be used in DMs.*")

    if not vc:
        return await ctx.send("• *I'm not connected to a voice channel.*")

    channel_id = str(ctx.author.voice.channel.id)
    if vc.is_playing():
        if channel_id in loop_status:
            loop_status[channel_id] = not loop_status[channel_id]
            status = "enabled" if loop_status[channel_id] else "disabled"
            await ctx.send(f"• *Looping {status}.*")
        else:
            loop_status[channel_id] = True
            await ctx.send("• *Looping has been enabled.*")
    else:
        await ctx.send("• *There's no music playing to loop.*")

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Flame"))
    await wavelink.NodePool.create_node(
        bot=client,
        host="lavalink.jirayu.net",
        port=2334,
        password="youshallnotpass",
        https=False
    )
    
    client.load_extension("jishaku")
    
    Flame = Fore.RED
    os.system("clear")
    print(Fore.RED + r"""
┏━┓︱︱︱︱︱︱︱︱︱︱︱︱︱︱
┃━┫┏┓︱┏━┓︱┏━━┓┏━┓
┃┏┛┃┗┓┃╋┗┓┃┃┃┃┃┻┫
┗┛︱┗━┛┗━━┛┗┻┻┛┗━┛
                                                        """)
    print(f"{Flame}Logged In As {client.user.name}\nID - {client.user.id}")
    print(f"{Flame}Total servers ~ {len(client.guilds)}")
    print(f"{Flame}Total Users ~ {len(client.users)}")
    print(f"{Flame}Made by Flame nd Zera <3")

client.run("",bot=False) 
