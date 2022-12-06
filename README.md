# Flight Bot
The code behind Flight Bot. A Discord bot for monitoring specific flight and airport data for University of North Dakota Aerospace pilots!

### Contact Info
Coming Soon

## How to Host
### Using Screen
Screen Help: https://www.geeksforgeeks.org/screen-command-in-linux-with-examples/
### Enter and create a new Screen Session

```bash
screen -R <name screen whatever you want>
```

### Start Program

```bash
pipenv run python Flight_Bot.py
```

## Information
### ADS-B Data
ADS-B data is pulled from a local server, using a JSON file.
The ADS-B server is run using readsb and tar1090. The data is then pulled from the aircraft.json file.
