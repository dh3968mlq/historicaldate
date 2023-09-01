# historicaldate

A Python package for:

   * Date handling including support for BC dates and uncertainty
   * Creating graphical timelines of historical data. This uses *Plotly*, which gives zoom, pan, hovertext and hyperlink interactivity

See https://historicaldate.com/ for example outputs and an interactive timeline builder based on this package.

![Example timeline image](https://historicaldate.com/wp-content/uploads/2023/05/basic_timeline_example.png)

### Date handling

Flexible and natural date formats are supported. 
   * The default formats are variants of '25 Dec 1066' and '1066-12-25'
   * ... with options to recognise '25/12/1055', '12/25/1066' and 'Dec 25, 1066'
   * '1066' is treated as being an undetermined date in that year
   * 'circa' is allowed: e.g. 'circa 1028'
   * Uncertainty can be specified. e.g. 'Between 1025 and 1032'
   * BC dates are supported. e.g. 'circa 525 bc'

The basic ideas are:
   * An uncertain date is represented as three dates: the earliest possible, the midpoint and the latest possible
   * These are represented as (int) ordinals with non-positive values representing BC dates
   * AD dates are also represented as Python dates
   * The difference between Julian and Gregorian calendars is naively ignored - which doesn't matter to most expected users and makes everything much simpler

### To create a timeline:
   * Download this package from 
https://github.com/dh3968mlq/historicaldate
   * Download sample data from https://github.com/dh3968mlq/historicaldate-data, and/or
   * Create .csv files of data (see below for column names and date formats)
   * Create and run a Python program, similar to below, or see sample timeline code in the *timelines* folder in this repository

See https://historicaldate.com/ for example outputs and for an interactive timeline builder.

### Sample code:

```python
# Sample code for a timeline of British monarchs and Prime Ministers
# The folders that historicaldate and historicaldate-data have been downloaded to...
hdroot = "/svol1/pishare/users/pi/repos/timelines/historicaldate" 
dataroot = "/svol1/pishare/users/pi/repos/timelines/historicaldate-data" 
import sys
sys.path.append(hdroot)
from historicaldate import hdpl  # Timelines using Plotly
import pandas as pd

df1 = pd.read_csv(f"{dataroot}/data/history/europe/British Monarchs.csv",
                 na_filter=False)
df2 = pd.read_csv(f"{dataroot}/data/history/europe/British Prime Ministers.csv",
                 na_filter=False)

pltl = hdpl.plTimeLine()
pltl.add_event_set(df1, title="British Monarchs from 1066")
pltl.add_event_set(df2, title="British Prime Ministers") 
pltl.show() # Show in a browser, or...
pltl.write_html("/home/pi/example_timeline.html")
```

In the CSV files used here:
   * Dates are specified in natural text formats, allowing for uncertainty.
   * It's possible to specify a single date for an event...
   * ... or start and end dates of persistent events, such as a US presidency or a British monarch's reign...
   * ... and/or birth and death dates of persons
   
In the timeline display:
   * A person's life is displayed as a dotted line
   * An event is displayed as a diamond symbol, or two diamonds linked by a solid line if it persists over time
   * Uncertainty in dates is displayed as thin lines

## Input file format

Dataframes passed to *add_event_set* have one row per event or life, and specific column names. *label* must be present, together with either *hdate* or both of *hdate_birth* and *hdate_death*. All other columns are optional.

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
| rank | An integer, use together with *max_rank* to control which rows are displayed

## Date formats

**Two core formats are supported by default**
   * 25 Dec 1066 (or variants such as 25th Dec 1066 or 25 December 1066 etc.)
   * 1066-12-25

**Additional formats are also supported**

```python
pltl = hdpl.plTimeLine(dateformat="dmy")
```

Specifying *dateformat="dmy"* also allows...
   * 25/12/1066

```python
pltl = hdpl.plTimeLine(dateformat="mdy")
```

Specifying *dateformat="mdy"* allows...
   * 12/25/1066
   * Dec 25, 1066

But does not allow...
   * 25/12/1066
   * 25 Dec 1066

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

A date such as *circa 1066* leads to uncertainty, of a few years, being shown on the timeline as a thin line.

**The difference between Julian and Gregorian calendars is (as yet) ignored**

Python dates are used for AD (CE) timeline displays,
and *25 Dec 1066* converts to the Python date *1066-12-25*.

This gets us into the tricky question of the few days difference between the Julian and Gregorian calendars. The philosophy adopted here is (at least for the moment) to observe that this difference doesn't have any significant impact on almost all timeline displays, and so can be ignored.

In effect this package naively assumes that any AD date string passed to *HDate* is (proleptic) Gregorian, the same assumption that is made by Python's *datetime.date*.
This is 'naive' because the usual convention when quoting historical dates is to use the calendar in operation at the relevant place at the time. So when we say that the coronation of William I of England took place on 25 Dec 1066, that is a Julian date, not a proleptic Gregorian date (which I believe would be 31 Dec 1066).

It's expected this approach will continue to be the default, since to do anything else would make things unnecessarily more complex for users. It's possible however that Julian / Gregorian conversion functionality may be added to future versions

(*Proleptic Gregorian Calendar*: A Gregorian calendar extended backwards in time before the dates, starting in the 16th century AD, that the Gregorian calendar was actually introduced)

## Dealing with dates - the HDate() object class

The underlying date processing uses the object class *historicaldate.hdate.HDate()*

The constructor takes a string as input, and the object has a property *pdates*, a dictionary encoding the date information.

```python
>>>from historicaldate import hdate
>>>hd1 = hdate.HDate('Dec 1066')
>>>print(hd1.pdates)
{'mid': datetime.date(1066, 12, 15), 'ordinal_mid': 389332, 'slmid': 'm', 
 'late': datetime.date(1066, 12, 31), 'ordinal_late': 389348, 'sllate': 'm',
 'early': datetime.date(1066, 12, 1), 'ordinal_early': 389318, 'slearly': 'm'}
>>>hd2 = hdate.HDate('Dec 20, 1066', dateformat="mdy")
>>>print(hd2.pdates)
{'mid': datetime.date(1066, 12, 20), 'ordinal_mid': 389337, 'slmid': 'd',
 'late': datetime.date(1066, 12, 20), 'ordinal_late': 389337, 'sllate': 'd',
 'early': datetime.date(1066, 12, 20), 'ordinal_early': 389337, 'slearly': 'd'}
>>>hd3 = hdate.HDate('385 BC')
>>> print(hd3.pdates)
{'mid': None, 'ordinal_mid': -140455, 'slmid': 'y', 
 'late': None, 'ordinal_late': -140256, 'sllate': 'y', 
 'early': None, 'ordinal_early': -140621, 'slearly': 'y'}
```

All dates (AD and BC) are given values of *ordinal_early*, *ordinal_mid* and *ordinal_late*. These represent the earliest possible, midpoint and latest possible ordinals (int) corresponding to the date specified.

These are usual Python date ordinals (int) for AD dates as created by *datetime.date.toordinal()*, extended backwards in time to non-positive numbers for BC dates assuming that 1BC, 5BC etc. are leap years. See below for how the few days difference between the Julian and Gregorian calendars is treated.

AD dates are also given values of *early*, *mid* and *late*, which are the equivalent Python dates (*datetime.date* objects).

The dictionary members *slearly*, *slmid* and *sllate* indicate the 'specification level' of the corresponding date, and take the following values:

| Value | Meaning |
| ------ | ----- |
| 'd'   | day  |
| 'm'   | month  |
| 'y'   | year  |
| 'c'   | Derived from a 'circa' calculation  |
| 'o'   | Derived from an 'ongoing' calculation  |

# Package Documentation

## *plTimeLine()* object: timelines using Plotly

**Constructor arguments**

*pltl = hdpl.plTimeLine(self, title=None, mindate=None, maxdate=None, 
                hovermode='closest', hoverdistance=5, xmode="date", dateformat=None)*

| Parameter | Usage | Default |
| ------ | ----- | ----- |
| title: str   | Title displayed on timeline  | No title |
| mindate: datetime.date | Initial earliest date displayed  | 200 years before today()
| maxdate: datetime.date   | Initial latest date displayed  | 10 years after today() |
| hovermode: str   | Can be 'closest', 'x' or 'x unified' See https://plotly.com/python/hover-text-and-formatting/  | 'closest' |
| hoverdistance: int   | See https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html  | 5 |
| xmode: str | Controls how X-axis values are displayed. If *xmode='date'* X-axis values are displayed as Python *datetime.date* values, and BC dates are ignored. If *xmode='years'* X-axis values are displayed as years as *float* values, and both AD and BC dates can be displayed. | 'date' |
| dateformat | If *None*, date formats accepted are variants of *25 Dec 1066* and *1066-12-25*. If *dateformat='dmy'* then *25/12/1066* is also accepted. If *dateformat='mdy'* then *12/25/1066*, *Dec 25 1066* and *1066-12-25* are accepted, but *25 Dec 1066* is not accepted. | None |


## *plTimeLine()* Methods

### *pltl.fit_xaxis(self, mindate=None, maxdate=None)*

Fit x axis to specified dates, or to the date range of the data currently displayed.

*mindate* and *maxdate* may be passed as either a Python date (datetime.date), an ordinal (int) (which may be less than zero if xmode='years') or as a date string (str) in a format acceptable to HDate. 

### *pltl.add_event_set(df, title="", showbirthanddeath=True, showlabel=True, lives_first=True,  rowspacing=0.3, hover_datetype='day', study_range_start=None, study_range_end=None, max_rank=1)*

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
| study_range_start| Start of study range. Events lying entirely before this date will be ignored. May be passed as either a Python date (datetime.date), an ordinal (int) (which may be less than zero if xmode='years') or as a date string (str) in a format acceptable to HDate |
| study_range_end: datetime.date | End of study range. Events lying entirely after this date will be ignored. May be passed as either a Python date (datetime.date), an ordinal (int) (which may be less than zero if xmode='years') or as a date string (str) in a format acceptable to HDate |
| max_rank: int | Indicates the maximum value of the *rank* column in input data that will be displayed. Default 1 |

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

## *hdpl* utility functions

### *added, message = hdpl.check_dataframe(df, study_range_start=None, study_range_end=None, dateformat="default")*

Checks if a data frame can be used by *add_event_set()*.

*added* is a bool indicating if events from the dataframe can be added.

*message* indicates a reason if *added* is False. This function traps all errors and returns them formatted in *message*

## The HDate object

### Constructor arguments

*hd = hdate.HDate(hdstr="", missingasongoing=False, dateformat=None)*

hdstr : The input date string. See above for allowed formats

missingasongoing : determines if a blank string is interpreted as 'ongoing' or (equivalently) 'alive'

dateformat : may be None, "dmy" or "mdy". See above for how this affects the accepted date formats.

## *hdate* utility functions

In all *hdate* utility functions 
   * The parameter *date_or_ordinal* may be passed as either a Python date (datetime.date), an ordinal (int) (which may be less than zero) or as a date string (str) in a format acceptable to HDate.
   * The parameter *dateformat* is equivalent to the same parameter in the *HDate* constructor. See above for details.

#### *ord = to_ordinal(date_or_ordinal, delta=0, dateformat=None)*

Converts a date or ordinal value to an ordinal. 

*delta*: indicates a number of days to be added to the original date.

#### *pdate = to_python_date(date_or_ordinal, dateformat=None)*

Converts a date or ordinal value to a python date. 

Returns a *None* value if *date_or_ordinal* is BC.

#### *yrs = to_years(date_or_ordinal, dateformat=None)*

Converts a date or ordinal to an approximate number of years (float). The returned value 0.0 corresponds to ordinal value 0, which is 31st December, 1BC.

The implementation is approximate, but believed to be good enough for most timeline displays.

#### *syear = format_year(year, showzeroas1ad=True, adtext="AD", bctext="BC")*

Formats a year (int or float) in a way suitable for display on an X-axis that is showing dates as float values corresponding to years.

#### *ord = years_to_ordinal(years)*

Converts a year number (float) to an ordinal.

Also approximate, but an exact inverse of *to_years*

#### *ymd = to_ymd(date_or_ordinal, dateformat=None)*

Converts a date or ordinal to a named tuple containing year, month and day numbers

The tuple definition is:
```python
YMD = namedtuple("YMD", "year month day")
```

### ord = calc_mid_ordinal(hdstring, dateformat=None)

Returns the mid-point ordinal from a date held as a string in *HDate* format


## Changes

### New in 0.0.5

   * BC dates are now supported in *HDate*
   * Ordinal dates implemented in *HDate*
   * *dateformat* implemented, allowing dates to be formatted as *25/12/1066* or *12/25/1066* or *Dec 25, 1066*
   * BC dates can now be displayed on timelines (*xmode=years*)
   * X-axis (date axis) labels moved to top 

### New in 0.0.4

*add_event_set()* now updates yaxes to fit the displayed data

New method *plTimeLine().fit_xaxis(self, mindate=None, maxdate=None)* that fits the X axis either to the data or to a specified range of dates

X axis date labels moved to top of display

Study range filtering added, parameters *study_range_start* and *study_range_end* of the *add_event_set* method. Event sets lying entirely outside the study range are not displayed.

Filtering on the value of a *rank* column in input data, parameter *max_rank* of the *add_event_set* method. 

### New in 0.0.3

   * New English Football timeline code (*english_football.py*)
   * New *hover_datetype* parameter to *add_event_set*
   * New *htext_end* column supported
   