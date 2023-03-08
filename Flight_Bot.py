#import requests
import config
from flight_data import *
import time
import requests
import json
from contextlib import closing
import urllib.request
from urllib.request import urlopen, URLError
import discord
from discord import app_commands
from discord.ext import commands, tasks
from bs4 import BeautifulSoup


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

# ADS-B Storage
calllast = "None"
loopcount = 0

# Making the bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

@bot.event
async def on_ready():
    #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Flight Restrictions"))
    await bot.change_presence(activity=discord.CustomActivity(name="Flight Restrictions"))
    data_collection.start()
    adsb_loop.start()
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} commands synced!")
    except:
        print("A sync error occured")
    test_ch = bot.get_channel(1044129340432056361)
    await test_ch.send(f"***{bot.user} has Started***")
    await test_ch.send(f"{len(synced)} commands synced")


    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

    if bot.user.mentioned_in(message):
        await message.channel.send("Hello!\nYou can type `!help` for more info")

@bot.tree.command(name="metar", description="Get airport raw METAR data")
async def metar_cmd(interaction: discord.interactions, airport: str):
    url = f"https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString={airport}"
    if len(airport) < 4 or len(airport) > 4:
        await interaction.response.send_message("Please use four letter identifier. (Eg. KGFK & KRSW)")
        return
    try:
        metar = metar_raw(url)
        await interaction.response.send_message(metar)
        print("METAR Sent!")
        return
    except:
        await interaction.response.send_message("Airport not found :cry:")
        return

@bot.tree.command(name="status", description="Get Flight Bot status & ping")
async def status(interaction: discord.Integration):
    await interaction.response.send_message(f"Flight Bot is **ONLINE**! Ping: {round(bot.latency * 1000)}ms")

    print("Status Sent!")

@bot.tree.command(name="restrictions", description="Get current UND Flight Restrictions")
async def restrictions(interaction: discord.interactions):
    fr = flight_restrictions(fr_url)
    frf = f"**UND Flight Restrictions**\n> Fixed Wing: {fr[0]}\n> Helicopter: {fr[1]}\n> UAS: {fr[2]}"
    await interaction.response.send_message(frf)

@bot.tree.command(name="help", description="Shows info and commands")
async def help(interaction: discord.interactions):

    embed = discord.Embed(
        colour = discord.Colour.orange()
    )

    embed.set_author(name="Help")
    embed.add_field(name="Slash Commands", value="Look in the slash commands menu to see all commands", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="notes", description="Gets current flight restriction notes")
async def notes(interaction: discord.interactions):
    data = fr_notes_all(fr_url)
    none = "No current flight restriction notes"
    i = 1
    embed = discord.Embed(
        colour = discord.Colour.blue()
    )
    embed.set_author(name="Flight Restriction Notes")
    if data[0] <= 2:
        embed.add_field(name=f"None", value=none, inline=False)
    else:
        while i <= data[0] - 2:
            embed.add_field(name=f"Note {i}", value=data[i], inline=False)
            i += 1
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="staff", description="Gets current airport staff")
async def staff(interaction: discord.interactions):
    count = fr_notes_count(fr_url)
    mod_n = count - 1
    mod = fr_notes_b(fr_url, mod_n)
    sof = fr_notes_b(fr_url, count)

    embed = discord.Embed(
        colour = discord.Colour.blue()
    )
    embed.set_author(name="Airport Staff")
    embed.add_field(name=f"MOD:", value=mod, inline=False)
    embed.add_field(name=f"SOF:", value=sof, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="update", description="Updates current flight restriction notifications")
@commands.has_permissions(administrator=True)
async def update(interaction: discord.interactions):
    global fixedwing_last
    global helicopter_last
    global uas_last

    fixedwing_last = 1
    helicopter_last = 1
    uas_last = 1

    await interaction.response.send_message("Flight Restrictions Updating...")

@bot.command()
@commands.has_permissions(administrator=True)
#@commands.has_any_role("Big Cheese", "Medium Cheese")
async def count(ctx):
    count = fr_notes_count(fr_url)
    data = fr_notes_all(fr_url)
    await ctx.send(f"Count: {count} Notes: {data[0]}")

@bot.command()
@commands.has_permissions(administrator=True)
async def servers(ctx):
  servers = list(bot.guilds)
  await ctx.send(f"Connected on {str(len(servers))} servers:")
  await ctx.send('\n'.join(guild.name for guild in servers))

@bot.tree.command(name="pa", description="Get an airports pressure elivation")
async def pa(interaction: discord.interactions, airport: str):
    pa = pressure_altitude(airport)
    await interaction.response.send_message(pa)

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
        if fixedwing_last == " ":
            # Storing last posted values
            fixedwing_last = fr_live[0]
        else:
            # Storing last posted values
            fixedwing_last = fr_live[0]
            # Posting to FR Fixed Wing channel
            await fixedwing_ch.send(fixedwing)

    # Helicopter Flight Restrictions
    if fr_live[1] != helicopter_last:
        if helicopter_last == " ":
            # Storing last posted values
            helicopter_last = fr_live[1]
        else:
            # Storing last posted values
            helicopter_last = fr_live[1]
            # Posting to FR Helicopter channel
            await helicopter_ch.send(helicopter)

    # UAS Flight Restrictions
    if fr_live[2] != uas_last:
        # Storing last posted values
        uas_last = fr_live[2]
        # Posting to FR UAS channel
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

@tasks.loop(seconds=60)
async def adsb_loop():
    global loopcount
    global calllast

    
    emergencies_ch = bot.get_channel(1048503422430744596)
    test_ch = bot.get_channel(1044129340432056361)

    squawks = [7500, 7600, 7700]

    if loopcount == 30:
        loopcount = 0
    else:
        loopcount += 1

    with closing(urlopen(config.adsb_url, None, 5.0)) as aircraft_file:
        aircraft_data = json.load(aircraft_file)
    
    for plane in aircraft_data['aircraft']:
        hex = plane.get('hex')
        lat = plane.get('lat')
        lon = plane.get('lon')
        squawk = plane.get('squawk')
        callsign = plane.get('flight')

        if callsign and lat and lon and squawk:
            if int(squawk) in squawks:
                if callsign == calllast:
                    break
                else:
                    calllast = callsign
                    loopcount = 0
                    output = f"""
<@&1082898378393931776>: **{callsign}** Squawking: {squawk}
ADS-B: https://adsb.nattech.xyz/?icao={hex}
"""

                await emergencies_ch.send(output)
            

bot.run(config.TOKEN)