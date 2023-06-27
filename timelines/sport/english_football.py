
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
def get_colxref(filename):
    df = pd.read_csv(f"{dataroot}/data/sport/football/{filename}")[["abbreviation","colour"]]
    df = df[df["colour"].notna()]
    df["abbreviation"] = df["abbreviation"].str.strip()
    return df
df_colxref = get_colxref("team_abbreviations.csv")
df_colxref_national = get_colxref("national_team_abbreviations.csv")

def read_file(filename, df_xref=None):
    "Read file and merge with colours cross-reference"
    df = pd.read_csv(filename, na_filter=False)
    if "abbreviation" in df.columns and df_xref is not None:
        df["abbreviation"] = df["abbreviation"].str.strip()
        if "colour" in df.columns:
            df = df.drop(columns="colour")
        df = df.merge(df_xref, on="abbreviation", how="left", validate="m:1")
        df["colour"] = df["colour"].fillna("black")
    return df

df_epl = read_file(f"{dataroot}/data/sport/football/english_premier_league.csv",
                   df_xref=df_colxref)
df_facup = read_file(f"{dataroot}/data/sport/football/fa_cup.csv",
                   df_xref=df_colxref)
df_ucl = read_file(f"{dataroot}/data/sport/football/uefa_champions_league.csv",
                   df_xref=df_colxref)
df_world = read_file(f"{dataroot}/data/sport/football/world_cup.csv",
                   df_xref=df_colxref_national)
df_euros = read_file(f"{dataroot}/data/sport/football/european_championship.csv",
                   df_xref=df_colxref_national)

pltl = hdpl.plTimeLine(mindate=datetime.date(1990,7,1), 
                       maxdate=datetime.date.today() + datetime.timedelta(days=400),
                       title="English Men's Club and International Football (since 1993)")
pltl.add_event_set(df_epl, title="Top Tier: Premier League", hover_datetype='year')
pltl.add_event_set(df_facup, title="FA Cup")
pltl.add_event_set(df_ucl, title="UEFA Champions League", hover_datetype='year')
pltl.add_event_set(df_world, title="FIFA World Cup")
pltl.add_event_set(df_euros, title="UEFA European Championships")
pltl.show() 

pltl.write_html("html/english_club_football.html")
