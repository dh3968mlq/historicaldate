
# The path this repo (https://github.com/dh3968mlq/historicaldate) has been downloaded to
hdroot = "/svol1/pishare/users/pi/repos/timelines/historicaldate"
# The path the data repo (https://github.com/dh3968mlq/historicaldate-data) has been downloaded to
dataroot = "/svol1/pishare/users/pi/repos/timelines/historicaldate-data"

import sys
sys.path.append(hdroot)
from historicaldate import hdpl
import pandas as pd

df0 = pd.read_csv(f"{dataroot}/data/history/europe/Six Wives of Henry VIII/Henry VIII.csv",
                 na_filter=False)
df1 = pd.read_csv(f"{dataroot}/data/history/europe/Six Wives of Henry VIII/Catherine of Aragon.csv",
                 na_filter=False)
df2 = pd.read_csv(f"{dataroot}/data/history/europe/Six Wives of Henry VIII/Anne Boleyn.csv",
                 na_filter=False)
df3 = pd.read_csv(f"{dataroot}/data/history/europe/Six Wives of Henry VIII/Jane Seymour.csv",
                 na_filter=False)
df4 = pd.read_csv(f"{dataroot}/data/history/europe/Six Wives of Henry VIII/Anne of Cleves.csv",
                 na_filter=False)
df5 = pd.read_csv(f"{dataroot}/data/history/europe/Six Wives of Henry VIII/Catherine Howard.csv",
                 na_filter=False)
df6 = pd.read_csv(f"{dataroot}/data/history/europe/Six Wives of Henry VIII/Catherine Parr.csv",
                 na_filter=False)

xmode = 'date'
xmode = 'years'
pltl = hdpl.plTimeLine(xmode=xmode)
pltl.add_event_set(df0, title="Henry VIII", showbirthanddeath=True)
pltl.add_event_set(df1,title="Catherine of Aragon")
pltl.add_event_set(df2,title="Anne Boleyn")
pltl.add_event_set(df3,title="Jane Seymour")
pltl.add_event_set(df4,title="Anne of Cleves")
pltl.add_event_set(df5,title="Catherine Howard")
pltl.add_event_set(df6,title="Catherine Parr")
pltl.fit_xaxis()
pltl.show() 

pltl.write_html("historicaldate/html/tl_ukhistory.html")
