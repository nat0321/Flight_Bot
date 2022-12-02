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

def fr_notes_b(url, line):
    line = int(line)
    line_c = line + 3
    selection = ".auto-style{}b".format(line_c)
    # Getting data
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')
    data = html.select(selection)[0].get_text()
    return data

def fr_notes_all(url):
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')

    output = [0]
    i =4
    while i < 10:
        selection = f".auto-style{i}"
        try:
            data = html.select(selection)[0].get_text()
        except IndexError:
            break
        output.append(data)
        i += 1
    output[0] = i - 4 #Kept changing this between 2 & 4 something not right
    return output

def fr_notes_count(url):
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')

    i = 4
    while i < 10:
        selection = f".auto-style{i}"
        try:
            data = html.select(selection)[0].get_text()
        except IndexError:
            break
        i += 1
    i = i - 4 #Kept changing this between 2 & 4 something not right
    return i

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

def pressure_altitude(url):
    # Replace other metar bot on home assistant
    data = "unavalible"
    # Pulling web XML file
    raw_xml = urllib.request.urlopen(url)
    raw_data = raw_xml.read()

    # Parsing XML file
    bs_data = BeautifulSoup(raw_data, "xml")

    # Pulling required data
    data = bs_data.find('altim_in_hg')
    if data is None:
        data = "unavalible"

    raw_xml.close()

    f_press = float(data.text)
    s_press = 29.92
    f_elev = 845

    press_c = f_press - s_press
    elev_c = press_c * 1000
    p_alt = elev_c + f_elev
    return p_alt