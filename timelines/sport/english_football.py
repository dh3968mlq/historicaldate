
# The path this repo (https://github.com/dh3968mlq/historicaldate) has been downloaded to
hdroot = "/svol1/pishare/users/pi/repos/timelines/historicaldate"
# The path the data repo (https://github.com/dh3968mlq/historicaldate-data) has been downloaded to
dataroot = "/svol1/pishare/users/pi/repos/timelines/historicaldate-data"

import sys
sys.path.append(hdroot)
from hdtimelines import pltimeline
import pandas as pd
import datetime

# Abbreviations and colours
def get_colxref(filename):
    df = pd.read_csv(f"{dataroot}/data/sport/football/reference_tables/{filename}")[["abbreviation","colour"]]
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

df_epl = read_file(f"{dataroot}/data/sport/football/English Premier League and First Division.csv",
                   df_xref=df_colxref)
df_facup = read_file(f"{dataroot}/data/sport/football/FA Cup.csv",
                   df_xref=df_colxref)
df_ucl = read_file(f"{dataroot}/data/sport/football/UEFA Champions League.csv",
                   df_xref=df_colxref)
df_world = read_file(f"{dataroot}/data/sport/football/FIFA World Cup.csv",
                   df_xref=df_colxref_national)
df_euros = read_file(f"{dataroot}/data/sport/football/European Championship.csv",
                   df_xref=df_colxref_national)

pltl = pltimeline.plTimeLine(mindate=datetime.date(1990,7,1), 
                       maxdate=datetime.date.today() + datetime.timedelta(days=400),
                       title="English Men's Club and International Football (since 1993)")
pltl.add_topic_from_df(df_epl, title="Top Tier: Premier League", hover_datetype='year')
pltl.add_topic_from_df(df_facup, title="FA Cup")
pltl.add_topic_from_df(df_ucl, title="UEFA Champions League", hover_datetype='year')
pltl.add_topic_from_df(df_world, title="FIFA World Cup")
pltl.add_topic_from_df(df_euros, title="UEFA European Championships")
pltl.show() 

pltl.write_html("historicaldate/html/english_club_football.html")
