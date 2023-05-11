# Sample code for a timeline of British monarchs and Prime Ministers
hdroot = "/svol1/pishare/users/pi/repos/historicaldate" # The folder historicaldate has been downloaded to
import sys
sys.path.append(hdroot)
from historicaldate import hdplotly as hdp
import pandas as pd

df = pd.read_csv(f"{hdroot}/data/history/europe/United Kingdom/British Monarchs.csv",
                 na_filter=False)
df2 = pd.read_csv(f"{hdroot}/data/history/europe/United Kingdom/British Prime Ministers.csv",
                 na_filter=False)

pltl = hdp.plTimeLine()
pltl.add_event_set(df, title="British Monarchs from 1066")
pltl.add_event_set(df2, title="British Prime Ministers") 
pltl.show() 