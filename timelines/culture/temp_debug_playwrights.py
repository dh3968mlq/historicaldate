
# The path this repo (https://github.com/dh3968mlq/historicaldate) has been downloaded to
hdroot = "/svol1/pishare/users/pi/repos/historicaldate"
# The path the data repo (https://github.com/dh3968mlq/historicaldate-data) has been downloaded to
dataroot = "/svol1/pishare/users/pi/repos/historicaldate-data"

import sys
sys.path.append(hdroot)
from historicaldate import hdpl
import pandas as pd
import datetime

df = pd.read_csv(f"{dataroot}/data/culture/western_canon/Playwrights.csv",
                 na_filter=False)
df = df[df["label"] == "John Webster"]
assert len(df) == 1

pltl = hdpl.plTimeLine(mindate=datetime.date(1800,1,1), maxdate=datetime.date(1870,1,1),
                       title="The Brontës")
pltl.add_event_set(df, title="Test", showbirthanddeath=True,
                   study_range_start=datetime.date(1000,1,1), study_range_end=datetime.date(2100,12,31)
                   )
pltl.show() 

pltl.write_html("html/tl_brontes.html")
