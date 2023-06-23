
# The path this repo (https://github.com/dh3968mlq/historicaldate) has been downloaded to
hdroot = "/svol1/pishare/users/pi/repos/historicaldate"
# The path the data repo (https://github.com/dh3968mlq/historicaldate-data) has been downloaded to
dataroot = "/svol1/pishare/users/pi/repos/historicaldate-data"

import sys
sys.path.append(hdroot)
from historicaldate import hdpl
import pandas as pd
import datetime

# Abbreviations and colours
df_colxref = pd.read_csv(f"{dataroot}/data/sport/football/team_abbreviations.csv")[["abbreviation","colour"]]
df_colxref = df_colxref[df_colxref["colour"].notna()]
df_colxref["abbreviation"] = df_colxref["abbreviation"].str.strip()

def read_file(filename):
    "Read file and merge with colours cross-reference"
    df = pd.read_csv(filename, na_filter=False)
    if "abbreviation" in df.columns:
        df["abbreviation"] = df["abbreviation"].str.strip()
        if "colour" in df.columns:
            df = df.drop(columns="colour")
        df = df.merge(df_colxref, on="abbreviation", how="left", validate="m:1")
        df["colour"] = df["colour"].fillna("black")
    return df

df_epl = read_file(f"{dataroot}/data/sport/football/english_premier_league.csv")
df_facup = read_file(f"{dataroot}/data/sport/football/fa_cup.csv")
df_ucl = read_file(f"{dataroot}/data/sport/football/uefa_champions_league.csv")

pltl = hdpl.plTimeLine(mindate=datetime.date(1990,7,1), 
                       maxdate=datetime.date.today() + datetime.timedelta(days=400),
                       title="English Club Football")
pltl.add_event_set(df_epl, title="Top Tier: Premier League", hover_datetype='year')
pltl.add_event_set(df_facup, title="FA Cup")
pltl.add_event_set(df_ucl, title="UEFA Champions League", hover_datetype='year')
pltl.show() 

pltl.write_html("html/english_club_football.html")
