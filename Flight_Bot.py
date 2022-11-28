#import requests
from flight_data import *
import time
import requests
import urllib.request
import discord
from discord.ext import commands, tasks
from discord_webhook import DiscordWebhook
from bs4 import BeautifulSoup

# bot link
# https://discord.com/api/oauth2/authorize?client_id=1045095473884700752&permissions=412317370432&scope=bot%20applications.commands
TOKEN = 'MTA0NTA5NTQ3Mzg4NDcwMDc1Mg.G9Ukzv.qWGxNMkna8qtYFtBgkAnh7PzoQlh0lEkhB2vco'

# AWC Text Data Server URLs
gfk_url = "https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=KGFK"
rdr_url = "https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=KRDR"
ckn_url = "https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=KCKN"
gaf_url = "https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=KGAF"

# Flight Restrictions URL
fr_url = "https://aims-asp.aero.und.edu/sof2/sof2.aspx?site=U"

# Making Varables
gfk = []
rdr = []
ckn = []
gaf = []

# Making Storage
gfk_last = []
rdr_last = []
ckn_last = []
gaf_last = []
fixedwing_last = " "
helicopter_last = " "
uas_last = " "
gfk_raw_last = " "
autowx_time_last = 9999

# Making the bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Flight Restrictions"))
    data_collection.start()
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

    
    username = str(message.author.name)
    user_message = str(message.content)
    channel = str(message.channel.name)

@bot.command(aliases=["STATUS"])
async def status(ctx):
    await ctx.send(f"Flight Bot is **ONLINE**! Ping: {round(bot.latency * 1000)}ms")

    print("Status Sent!")

@bot.command(aliases=["metar", "METAR"])
async def metar_cmd(ctx, *, airport):
    url = f"https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString={airport}"
    if len(airport) < 4 or len(airport) > 4:
        await ctx.send("Please use four letter identifier. (Eg. KGFK & KRSW)")
        return
    try:
        metar = metar_raw(url)
        await ctx.send(metar)
        print("METAR Sent!")
        return
    except:
        await ctx.send("Airport not found :cry:")
        return

@bot.command()
async def restrictions(ctx):
    fr = flight_restrictions(fr_url)
    frf = f"**UND Flight Restrictions**\n> Fixed Wing: {fr[0]}\n> Helicopter: {fr[1]}\n> UAS: {fr[2]}"
    await ctx.send(frf)

@bot.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    embed = discord.Embed(
        colour = discord.Colour.orange()
    )

    embed.set_author(name="Help")
    embed.add_field(name="!status", value="Returns bots status and ping time", inline=False)
    embed.add_field(name="!restrictions", value="Returns the current UND Flight Restrictions", inline=False)
    embed.add_field(name="!metar <ICAO Code>", value="Returns the current metar for the requested airport", inline=False)

    await ctx.author.send(embed=embed)


@bot.command()
async def meow(ctx):
    await ctx.send("Hello Tatanka!")

@tasks.loop(seconds=60)
async def data_collection():
    # Defining Global Varables
    global gfk
    global rdr
    global ckn
    global gaf
    global gfk_last
    global rdr_last
    global ckn_last
    global gaf_last
    global fixedwing_last
    global helicopter_last
    global uas_last
    global gfk_raw_last
    global autowx_time_last

    # Discord Channels
    test_ch = bot.get_channel(1044129340432056361)
    fixedwing_ch = bot.get_channel(986657152301154304)
    helicopter_ch = bot.get_channel(1000226423719592017)
    uas_ch = bot.get_channel(986722254639489164)
    autowx_ch = bot.get_channel(1014962694387941467)

    # Clearing lists
    gfk.clear()
    rdr.clear()
    ckn.clear()
    gaf.clear()

    # Pulling METAR data for each airport
    gfk = metar(gfk_url)
    rdr = metar(rdr_url)
    ckn = metar(ckn_url)
    gaf = metar(gaf_url)
    gfk_raw = metar_raw(gfk_url)

    # Pulling flight restriction data
    fr_live = flight_restrictions(fr_url)
    autowx_time = fr_autowx(fr_url, 5)

    # Formating Outputs
    localwx = "**Local Weather**\n> **KGFK:**  {} (Wind: {}@{}Kt Vis: {}SM)\n> **KRDR:**  {} (Wind: {}@{}Kt Vis: {}SM)\n> **KCKN:**  {} (Wind: {}@{}Kt Vis: {}SM)\n> **KGAF:**  {} (Wind: {}@{}Kt Vis: {}SM)".format(gfk[0], gfk[1], gfk[2], gfk[3],rdr[0], rdr[1], rdr[2], rdr[3],ckn[0], ckn[1], ckn[2], ckn[3],gaf[0], gaf[1], gaf[2], gaf[3])
    fixedwing = "<@&986672387040874577>: {}".format(fr_live[0])
    helicopter = "<@&986723294742986792>: {}".format(fr_live[1])
    uas = "<@&986723383976796210>: {}".format(fr_live[2])
    autowx = "<@&1014969092102430791>: Auto Weather active till {}LCL".format(autowx_time[1])
    autowx_day = "<@&1014969092102430791>: Auto Weather active till {}".format(autowx_time[1])

    # Testing for changes to data and updating Discord if data has changed
    # Fixed Wing Flight Restrictions
    if fr_live[0] != fixedwing_last:
        # Storing last posted values
        fixedwing_last = fr_live[0]

        await fixedwing_ch.send(fixedwing)

    # Helicopter Flight Restrictions
    if fr_live[1] != helicopter_last:
        # Storing last posted values
        helicopter_last = fr_live[1]

        await helicopter_ch.send(helicopter)

    # UAS Flight Restrictions
    if fr_live[2] != uas_last:
        # Storing last posted values
        uas_last = fr_live[2]

        await uas_ch.send(uas)

    # AutoWX Flight Restrictions
    if autowx_time[0] == 'True' and autowx_time != autowx_time_last:
        autowx_time_last = autowx_time
        if autowx_time[1] == "end of day":
            await autowx_ch.send(autowx_day)
        else:
            await autowx_ch.send(autowx)

    # GFK Raw METAR
    if gfk_raw != gfk_raw_last:
        gfk_raw_last = gfk_raw

        await test_ch.send(gfk_raw)

    # Local Weather Channel
    if gfk != gfk_last or rdr != rdr_last or ckn != ckn_last or gaf != gaf_last:
            
        # Storing Last Posted Values
        gfk_last = gfk
        rdr_last = rdr
        ckn_last = ckn
        gaf_last = gaf


bot.run(TOKEN)
