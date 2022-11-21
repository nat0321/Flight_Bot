# UND Aerospace Discord
# Local Weather Automation
# Nicolo Taylor
# nicolo.taylor@und.edu

#import requests
import time
import requests
import urllib.request
from discord_webhook import DiscordWebhook
from bs4 import BeautifulSoup

def notify_discord(destination, message):
    webhook = DiscordWebhook(url=destination, content=message)
    response = webhook.execute()

def metar(url):
    data = []
    # Pulling web XML file
    raw_xml = urllib.request.urlopen(url)
    raw_data = raw_xml.read()

    # Parsing XML file
    bs_data = BeautifulSoup(raw_data, "xml")

    # Pulling required data
    fc = bs_data.find('flight_category')
    wd = bs_data.find('wind_dir_degrees')
    ws = bs_data.find('wind_speed_kt')
    vis = bs_data.find('visibility_statute_mi')

    # Pulling required text and checking for missing data
    if fc is None:
        data.append("Unknown")
    else:
        data.append(fc.text)
    if wd is None:
        data.append("Unknown")
    else:
        data.append(wd.text)
    if ws is None:
        data.append("Unknown")
    else:
        data.append(ws.text)
    if vis is None:
        data.append("Unknown")
    else:
        data.append(vis.text)

    # Closing XML file
    raw_xml.close()

    return data

def metar_raw(url):
    # Replace other metar bot on home assistant
    data = "unavalible"
    # Pulling web XML file
    raw_xml = urllib.request.urlopen(url)
    raw_data = raw_xml.read()

    # Parsing XML file
    bs_data = BeautifulSoup(raw_data, "xml")

    # Pulling required data
    data = bs_data.find('raw_text')

    raw_xml.close()

    return data.text

def flight_restrictions(url):
    output = []
    # Getting data
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')
    data = html.select('.auto-style1b')[0].get_text()
    output.append(data)
    data = html.select('.auto-style2b')[0].get_text()
    output.append(data)
    data = html.select('.auto-style3b')[0].get_text()
    output.append(data)
    return output

def fr_fixed_wing(url):
    # Getting data
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')
    data = html.select('.auto-style1b')[0].get_text()
    return data

def fr_helicopter(url):
    # Getting data
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')
    data = html.select('.auto-style2b')[0].get_text()
    return data

def fr_uas(url):
    # Getting data
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')
    data = html.select('.auto-style3b')[0].get_text()
    return data

def fr_notes(url, line):
    line = int(line)
    line_c = line + 3
    selection = ".auto-style{}".format(line_c)
    # Getting data
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')
    data = html.select(selection)[0].get_text()
    return data

def fr_autowx(url, count):
    i = 4
    count = int(count) + 4
    result = ["False", 9999]
    # Strings to test agiants
    autowx = "at or before"
    eod = "rest of the"
    test = "removed"

    # Getting data
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')

    # Testing each line
    while i < count:
        selection = ".auto-style{}".format(i)
        try:
            data = html.select(selection)[0].get_text()
        except IndexError:
            data = "Empty"

        # AutoWX Time
        if autowx in data:
            result[0] = "True"
            data = data.split(" ")
            data = data[9]
            data = data.split(",")
            result[1] = int(data[0])
            return result
        # AutoWX end of day
        elif eod and test in data:
            result[0] = "True"
            result[1] = "End of Day"
            return result
        i += 1
    return "False"

# Main Function
# Discord Webhook URLs
test_url = "https://ptb.discord.com/api/webhooks/1044129561455112225/K0W5IOj2_i6f2JjSw6NrWDR0huRxus3RVSiN2HCEBF1JTahK1fsyya7kw061gP6BvzLJ"
localwx_url = "https://ptb.discord.com/api/webhooks/1042925802897019042/TtVMWLJ31Pklta45lCcxD1U_7bk9bV2vwIx9yhsGGWY4Lfs5TtoC-L7OjFpjs3k213wo"
fr_fixed_wing_url = "https://ptb.discord.com/api/webhooks/986658093997891625/HOuVGxp1mZ5ska5o1dSWkvyMoKd2P10taXkEVVcbjbKzUJctfgeQLY14jonqDhl9jBxD"
fr_helicopter_url = "https://ptb.discord.com/api/webhooks/1000226481303191622/DzOnU1P76mO6lTKGvEzirGsVxon9mwbjatEVZVcgr4NZs1zBVqdXU0MBec_u0IRU4iKD"
fr_uas_url = "https://ptb.discord.com/api/webhooks/1000226561317945404/7a-R7291ycVlfMEBEI4LqomK-zL9ZrNzHtoce-ONIlqJpiAinCRBqxSP1Un72TEgr-Hi"
fr_autowx_url = "https://ptb.discord.com/api/webhooks/1014962731662704742/ITlfBlo4V_oOP-ETHjE3d6TMhoSj5F-Fx9bDCncVNeHUaI19VYmJoXCUSu8-57vaWWx4"

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
autowx_time_last = 9999

# Infinate loop to keep program always online
while True is True:
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

    # Pulling flight restriction data
    fr_live = flight_restrictions(fr_url)
    #fixedwing = fr_fixed_wing(fr_url)
    #helicopter = fr_helicopter(fr_url)
    #uas = fr_uas(fr_url)
    autowx_time = fr_autowx(fr_url, 5)

    # Formating Outputs
    localwx = "**Local Weather**\n> **KGFK:**  {} (Wind: {}@{}Kt Vis: {}SM)\n> **KRDR:**  {} (Wind: {}@{}Kt Vis: {}SM)\n> **KCKN:**  {} (Wind: {}@{}Kt Vis: {}SM)\n> **KGAF:**  {} (Wind: {}@{}Kt Vis: {}SM)".format(gfk[0], gfk[1], gfk[2], gfk[3],rdr[0], rdr[1], rdr[2], rdr[3],ckn[0], ckn[1], ckn[2], ckn[3],gaf[0], gaf[1], gaf[2], gaf[3])
    fixedwing = "<@&986672387040874577>: {}".format(fr_live[0])
    helicopter = "<@&986723294742986792>: {}".format(fr_live[1])
    uas = "<@&986723383976796210>: {}".format(fr_live[2])
    autowx = "Auto Weather active till {}LCL".format(autowx_time[1])

    # Testing for changes to data and updating Discord if data has changed
    # Fixed Wing Flight Restrictions
    if fr_live[0] != fixedwing_last:
        # Storing last posted values
        fixedwing_last = fr_live[0]

        notify_discord(fr_fixed_wing_url, fixedwing)

    # Helicopter Flight Restrictions
    if fr_live[1] != helicopter_last:
        # Storing last posted values
        helicopter_last = fr_live[1]

        notify_discord(fr_helicopter_url, helicopter)

    # UAS Flight Restrictions
    if fr_live[2] != uas_last:
        # Storing last posted values
        uas_last = fr_live[2]

        notify_discord(fr_uas_url, uas)

    # AutoWX Flight Restrictions
    if autowx_time[0] == 'True' and autowx_time != autowx_time_last:
        autowx_time_last = autowx_time
        notify_discord(fr_autowx_url, autowx)


    # Local Weather Channel
    if gfk != gfk_last or rdr != rdr_last or ckn != ckn_last or gaf != gaf_last:
        
        # Storing Last Posted Values
        gfk_last = gfk
        rdr_last = rdr
        ckn_last = ckn
        gaf_last = gaf

        #notify_discord(localwx_url, localwx)
    
    # Status Chek (Edit to Send Message every 6 hours at some point)
    status = "Server Online"
    notify_discord(test_url, status)

    # Wait 3 miutes than run agian
    time.sleep(180)