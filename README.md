# historicaldate

An open source Python package for creating interactive graphical timelines of historical data.

![Example timeline image](https://historicaldate.com/wp-content/uploads/2023/05/basic_timeline_example.png)

To create a timeline:
   * Download this package from 
https://github.com/dh3968mlq/historicaldate
   * Download sample data from https://github.com/dh3968mlq/historicaldate-data, and/or
   * Create .csv files of data (see below for column names and date formats)
   * Create and run a Python program, similar to below, or see sample timeline code in the *timelines* folder in this repository

See https://historicaldate.com/ for example outputs

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
   * Dates are specified in natural text formats, allowing for uncertainty. '25 Dec 1066', 'Dec 1066','1066' and 'Circa 1066' are all allowed (see below for details of date formats)
   * Data can be held in .csv files (see below for column names)
   * It's possible to specify a single date for an event...
   * ... or start and end dates of persistent events, such as a US presidency or a British monarch's reign...
   * ... and/or birth and death dates of persons
   * There is support for easily displaying timelines of events using *Plotly* which gives basic interactivity: zoom, pan, hovertext and hyperlinks
   
In the timeline display:
   * A person's life is displayed as a dotted line
   * An event is displayed as a diamond symbol, or two diamonds linked by a solid line if it persists over time
   * Uncertainty in dates is displayed as thin lines

## Input file format

Dataframes passed to *add_event_set* have one row per event or life, and specific column names. *label* must be present, togther with either *hdate* or both of *hdate_birth* and *hdate_death*. All other columns are optional.

| Column | Usage |
| ------ | ----- |
| label   | Event label, appears on the timeline  |
| description | Extended description, used for hovertext |
| hdate | Date of event, or start date if it is a persistent event |
| hdate_end | End date of a persistent event |
| hdate_birth | A person's birth date |
| hdate_death | A person's date of death, defaults to *alive* if *hdate_birth* is present|
| htext_end | Hover text linked to the marker drawn at *hdate_end* |
| color (or colour) | Colour to draw the event or life
| url | hyperlink, active by clicking on the displayed label |

## Date formats

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

A date such as *circa 1066* leads to undertainty, of a few years, being shown on the timeline as a thin line.

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

The dictionary members *slearly*, *slmid* and *sllate* indicate the 'specification level' of the corresponding date, and take the following values:

| Value | Meaning |
| ------ | ----- |
| 'd'   | day  |
| 'm'   | month  |
| 'y'   | year  |
| 'c'   | Derived from a 'circa' calculation  |
| 'o'   | Derived from an 'ongoing' calculation  |

## Package Documentation

### *plTimeLine()* object: timelines using Plotly

**Constructor arguments**

*pltl = hdpl.plTimeLine(title=None, mindate=None, maxdate=None, hovermode='closest', hoverdistance=5)*

| Parameter | Usage | Default |
| ------ | ----- | ----- |
| title: str   | Title displayed on timeline  | No title |
| mindate: datetime.date | Initial earliest date displayed  | 200 years before today()
| maxdate: datetime.date   | Initial latest date displayed  | 10 years after toay() |
| hovermode: str   | Can be 'closest', 'x' or 'x unified' See https://plotly.com/python/hover-text-and-formatting/  | 'closest' |
| hoverdistance: int   | See https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html  | 5 |

### Methods

### *pltl.add_event_set(df, title="", showbirthanddeath=True, showlabel=True, lives_first=True,  rowspacing=0.3)*

Add a set of events/lives held in a Pandas dataframe to a timeline display

| Parameter | Usage | Default |
| ------ | ----- | ----- |
| df : pandas.DataFrame | Dataframe to be displayed | (Required) |
| title: str   | Title displayed above this set of events  | No title |
| showbirthanddeath: bool | Whether birth and death values are shown | True |
| showlabel: bool | Whether the label of each event is displayed | True |
| lives_first: bool | Whether lives (rows with *hdate_birth* specified) are displayed above, and on separate lines from, oher events | True |
| rowspacing: float | Space between rows | 0.3 |
| hover_datetype: str | Specifies the precision to which dates in hover text are displayed. Must be one of 'day' (default), 'month' or 'year' |

### *pltl.show(fix_y_range=False)*

Displays the timeline (in a Jupyter Notebook or in a browser)

| Parameter | Usage | Default |
| ------ | ----- | ----- |
| fix_y_range: bool | Prevents zooming on Y axis | False |

### *pltl.write_html(filename, fix_y_range=False)*

Writes HTML file of the timeline

| Parameter | Usage | Default |
| ------ | ----- | ----- |
| filename: str | Name of file to create | (Required) |
| fix_y_range: bool | Prevents zooming on Y axis | False |

## Limitations

This is an early (0.0.2) release, and much remains to be done.

At present dates BC (BCE) are not supported, since date representation depends on Python *datetime.date* dates, which have this same limitation.

Support for date formats DD/MM/YYYY or MM/DD/YYYY is also as yet not supported. If implemented they are expected to be non-default formats, because of the risk of confusion between them.

## Changes

### New in 0.0.3

   * New English Football timeline code (*english_football.py*)
   * New *hover_datetype* parameter to *add_event_set*
   * New *htext_end* column supported
   