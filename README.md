# historicaldate

An open source package for creating timelines
of historical data.

Download from 
https://github.com/dh3968mlq/historicaldate

Sample code:

```python
# The folder historicaldate has been downloaded to...
hdroot = "/svol1/pishare/users/pi/repos/historicaldate" 
import sys
sys.path.append(hdroot)
from historicaldate import hdpl  # Timelines using Plotly
import pandas as pd

df1 = pd.read_csv(f"{hdroot}/data/history/europe/United Kingdom/British Monarchs.csv",
                 na_filter=False)
df2 = pd.read_csv(f"{hdroot}/data/history/europe/United Kingdom/British Prime Ministers.csv",
                 na_filter=False)

pltl = hdpl.plTimeLine()
pltl.add_event_set(df1, title="British Monarchs from 1066")
pltl.add_event_set(df2, title="British Prime Ministers") 
pltl.show() 
```

The basic ideas here are:
   * Dates are specified in natural text formats, allowing for uncertainty, usually in .csv files
   * Can specify start and end of persistent events, such as a US presidency or a British monarch's reign...
   * ... Or a single date for an event
   * Can specify birth and death dates of persons
   * Support for easily displaying timelines of events using *Plotly*...
   * ... which gives basic interactivity: zoom, pan, hovertext and hyperlinks
   * Some useful data files held in the repository
   
## Input file format

Dataframes passed to *add_event_set* have one row per event and specific column names. *label* must be present, togther with either *hdate* or both of *hdate_birth* and *hdate_death*. All other columns are optional.

| Column | Usage |
| ------ | ----- |
| label   | Event label, appears on the timeline  |
| description | Extended description, used for hovertext |
| hdate | Date of event, or start date if it is a persistent event |
| hdate_end | End date of a persistent event |
| hdate_birth | A person's birth date |
| hdate_death | A person's date of death, defaulst to *alive*|
| color (or colour) | Colour to draw the event
| url | hyperlink, active by clicking on the dispayed label |

## Date formats

The basics are:

**Two core formats are supported**
   * 25 Dec 1066 (or 25th Dec 1066 or 25 December 1066 etc.)
   * 1066-12-25

**The exact date is not required**

These are all allowed:
   * Dec 1066
   * 1066
   * 1066-12
   * circa 1066 (or c. 1066)
   * between 1066 and 1068
   * circa 1483 earliest 1483 (the death of Edward V of England)

**Python dates are used in a naive sort of way**

Python dates are used for AD (CE) timeline displays,
and *25 Dec 1066* converts to the Python date *1066-12-25*.

Stricly speaking this isn't quite right, since in usual
convention *25 Dec 1066* (the coronation of King William I of England) is a Julian Calendar date, while Python dates
are supposed to be in the Gregorian calendar, or at least
a 'proleptic' version of it - that is, extended backwards
in time before the date it was introduced.

This hardly ever matters, however, and it's 
generally less confusing to take the naive route.

