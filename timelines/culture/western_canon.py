
# The path this repo (https://github.com/dh3968mlq/historicaldate) has been downloaded to
hdroot = "/svol1/pishare/users/pi/repos/timelines/historicaldate"
# The path the data repo (https://github.com/dh3968mlq/historicaldate-data) has been downloaded to
dataroot = "/svol1/pishare/users/pi/repos/timelines/historicaldate-data"

import sys
sys.path.append(hdroot)
from historicaldate import hdpl
import pandas as pd
import datetime

df_monarchs = pd.read_csv(f"{dataroot}/data/history/europe/United Kingdom/British Monarchs.csv",
                 na_filter=False)
df_playwrights = pd.read_csv(f"{dataroot}/data/culture/western_canon/Playwrights.csv",
                 na_filter=False)
#df_playwrights = pd.read_csv(f"{dataroot}/data/culture/western_canon/greek_playwrights.csv",
#                 na_filter=False)
df_authors = pd.read_csv(f"{dataroot}/data/culture/western_canon/Authors.csv",
                 na_filter=False)
df_composers = pd.read_csv(f"{dataroot}/data/culture/western_canon/Classical Composers.csv",
                 na_filter=False)

pltl = hdpl.plTimeLine(#mindate=datetime.date(1,1,1), maxdate=datetime.date(500,1,1),
                       title="Culture: Western Canon", xmode="years")
pltl.add_event_set(df_monarchs, title="British Monarchs", showbirthanddeath=True)
pltl.add_event_set(df_playwrights, title="Playwrights", showbirthanddeath=True)
pltl.add_event_set(df_authors, title="Authors", showbirthanddeath=True)
pltl.add_event_set(df_composers, title="Classical Composers", showbirthanddeath=True)
pltl.show() 

pltl.write_html("historicaldate/html/tl_western_canon.html")
