
# The path this repo (https://github.com/dh3968mlq/historicaldate) has been downloaded to
hdroot = "/svol1/pishare/users/pi/repos/timelines/historicaldate"
# The path the data repo (https://github.com/dh3968mlq/historicaldate-data) has been downloaded to
dataroot = "/svol1/pishare/users/pi/repos/timelines/historicaldate-data"

import sys
sys.path.append(hdroot)
from historicaldate import hdpl
import pandas as pd

df1 = pd.read_csv(f"{dataroot}/data/history/europe/British Monarchs.csv",
                 na_filter=False)
df2 = pd.read_csv(f"{dataroot}/data/history/europe/Events in British History.csv",
                 na_filter=False)
df3 = pd.read_csv(f"{dataroot}/data/history/europe/British Prime Ministers.csv",
                 na_filter=False)

xmode = 'date'
xmode = 'years'
pltl = hdpl.plTimeLine(xmode=xmode)
pltl.add_event_set(df1, title="British Monarchs from 1066", showbirthanddeath=True)
pltl.add_event_set(df2,title="Events in British History")
pltl.add_event_set(df3, title="British Prime Ministers") 
pltl.show() 

pltl.write_html("historicaldate/html/tl_ukhistory.html")
