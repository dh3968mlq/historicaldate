
# The path this repo (https://github.com/dh3968mlq/historicaldate) has been downloaded to
hdroot = "/svol1/pishare/users/pi/repos/historicaldate"
# The path the data repo (https://github.com/dh3968mlq/historicaldate-data) has been downloaded to
dataroot = "/svol1/pishare/users/pi/repos/historicaldate-data"

import sys
sys.path.append(hdroot)
from historicaldate import hdpl
import pandas as pd
import datetime

df_epl = pd.read_csv(f"{dataroot}/data/sport/football/english_premier_league.csv",
                 na_filter=False)
df_ucl = pd.read_csv(f"{dataroot}/data/sport/football/uefa_champions_league.csv",
                 na_filter=False)

pltl = hdpl.plTimeLine(mindate=datetime.date(1990,7,1), 
                       maxdate=datetime.date.today() + datetime.timedelta(days=400),
                       title="English Club Football")
pltl.add_event_set(df_epl, title="Top Tier: Premier League", hover_datetype='year')
pltl.add_event_set(df_ucl, title="UEFA Champions League", hover_datetype='year')
pltl.show() 

pltl.write_html("html/english_club_football.html")
