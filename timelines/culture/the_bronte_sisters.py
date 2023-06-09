
# The path this repo (https://github.com/dh3968mlq/historicaldate) has been downloaded to
hdroot = "/svol1/pishare/users/pi/repos/historicaldate"
# The path the data repo (https://github.com/dh3968mlq/historicaldate-data) has been downloaded to
dataroot = "/svol1/pishare/users/pi/repos/historicaldate-data"

import sys
sys.path.append(hdroot)
from historicaldate import hdpl
import pandas as pd
import datetime

df_charlotte = pd.read_csv(f"{dataroot}/data/culture/brontes/charlotte_bronte.csv",
                 na_filter=False)
df_emily = pd.read_csv(f"{dataroot}/data/culture/brontes/emily_bronte.csv",
                 na_filter=False)
df_anne = pd.read_csv(f"{dataroot}/data/culture/brontes/anne_bronte.csv",
                 na_filter=False)
df_other = pd.read_csv(f"{dataroot}/data/culture/brontes/other_brontes.csv",
                 na_filter=False)
df_history = pd.read_csv(f"{dataroot}/data/history/europe/United Kingdom/Major events in British History.csv",
                 na_filter=False)


pltl = hdpl.plTimeLine(mindate=datetime.date(1800,1,1), maxdate=datetime.date(1870,1,1),
                       title="The Brontës")
pltl.add_event_set(df_charlotte, title="Charlotte Brontë", showbirthanddeath=True)
pltl.add_event_set(df_emily,title="Emily Brontë")
pltl.add_event_set(df_anne, title="Anne Brontë") 
pltl.add_event_set(df_other, title="Brontë Family") 
pltl.add_event_set(df_history,title="Events in British History")
pltl.show() 

pltl.write_html("html/tl_brontes.html")
