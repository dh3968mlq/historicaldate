# historicaldate 0.0.2

An open source package for creating timelines
of historical data.

Download from 
https://github.com/dh3968mlq/historicaldate

The partner repo https://github.com/dh3968mlq/historicaldate-data has some example datasets in CSV format

Sample code:

```python
# Sample code for a timeline of British monarchs and Prime Ministers
# The folders that historicaldate and historicaldate-data have been downloaded to...
hdroot = "/svol1/pishare/users/pi/repos/historicaldate" 
dataroot = "/svol1/pishare/users/pi/repos/historicaldate-data" 
import sys
sys.path.append(hdroot)
from historicaldate import hdpl  # Timelines using Plotly
import pandas as pd

df1 = pd.read_csv(f"{dataroot}/data/history/europe/United Kingdom/British Monarchs.csv",
                 na_filter=False)
df2 = pd.read_csv(f"{dataroot}/data/history/europe/United Kingdom/British Prime Ministers.csv",
                 na_filter=False)

pltl = hdpl.plTimeLine()
pltl.add_event_set(df1, title="British Monarchs from 1066")
pltl.add_event_set(df2, title="British Prime Ministers") 
pltl.show() # Show in a browser, or...
pltl.write_html("/home/pi/example_timeline.html")
```

The basic ideas here are:
   * Dates are specified in natural text formats, allowing for uncertainty, usually in .csv files
   * Can specify start and end of persistent events, such as a US presidency or a British monarch's reign...
   * ... Or a single date for an event
   * Can specify birth and death dates of persons
   * Support for easily displaying timelines of events using *Plotly*...
   * ... which gives basic interactivity: zoom, pan, hovertext and hyperlinks
   * A few example data files are held in the repository
   
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
   * 25 Dec 1066 (or variants such as 25th Dec 1066 or 25 December 1066 etc.)
   * 1066-12-25

**The exact date is not required**

These are all allowed:
   * Dec 1066
   * 1066
   * 1066-12
   * circa 1066
   * c. 1066
   * between 1066 and 1068
   * circa 1483 earliest 1483

**Ongoing events, or lives, are supported**

A missing value of *hdeath_death* (if there is a value of *hdate_birth*), or a value of 'ongoing' in *hdate_end* leads to an indication on a timeline that an event is ongoing, or that a person is still alive.

**Imprecise dates are treated properly**

A date such as *circa 1066* leads to undertainty, of a few years, being shown on the timeline.

**Python dates are used in a naive sort of way**

Python dates are used for AD (CE) timeline displays,
and *25 Dec 1066* converts to the Python date *1066-12-25*.

Stricly speaking this isn't quite right, since in usual
convention *25 Dec 1066* (the coronation of King William I of England) is a Julian Calendar date, while Python dates
are supposed to be in the Gregorian calendar, or at least
a 'proleptic' version of it - that is, extended backwards
in time before the date it was introduced. 

This hardly ever matters, however, and it's 
much, much less confusing to take the naive route rather than
converting the (Julian) date *25 Dec 1066* to the equivalent
proleptic Gregorian date (*31 Dec 1066*) when using Python dates.

## Dealing with dates - the HDate() object class

The underlying date processing uses the object class *historicaldate.hdate.HDate()*

The constructor takes a string as input, and the object has a property *pdates*, a dictionary that indicates a range of python dates (represented as *datetime.date* objects)

```python
from historicaldate import hdate
hd = hdate.HDate('Dec 1066')
print(hd.pdates)
```

...produces:

```text
{'mid': datetime.date(1066, 12, 15),
  'slmid': 'm',
  'late': datetime.date(1066, 12, 31),
  'sllate': 'm',
  'early': datetime.date(1066, 12, 1),
  'slearly': 'm'}
  ```

The basic idea here is that the dict entries *early*, *mid* and *late* give the earliest possible, midpoint and latest possible Python dates corresonding to the date specified. These are then used by the timeline utility to indicate the range of uncertainty on the timeline.

## Limitations

This is an early (0.0.2) release, and much remains to be done.

At present dates BC (BCE) are not supported, since date representation depends on Python *datetime.date* dates, which have this same limitation.

Support for date formats DD/MM/YYYY or MM/DD/YYYY is also as yet not supported. If implemented they are expected to be non-default formats, because of the risk of confusion between them.

