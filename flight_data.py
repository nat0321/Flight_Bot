import requests
import urllib.request
from bs4 import BeautifulSoup

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
    if data is None:
        data = "unavalible"

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

def fr_notes(url, line):
    line = int(line)
    line_c = line + 3
    selection = ".auto-style{}".format(line_c)
    # Getting data
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')
    data = html.select(selection)[0].get_text()
    return data

def fr_notes_all(url):
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')

    while True:
        i = 3
        num = 0
        selection = ".auto-style{}".format(i)
        try:
            data[num] = html.select(selection)[0].get_text()
        except IndexError:
            count = i - 3
            return count, data
        i += 1


def fr_autowx(url, count):
    i = 4
    count = int(count) + 4
    result = ["False", 9999]
    # Strings to test against
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
            result[1] = "end of day"
            return result
        i += 1
    return "False"