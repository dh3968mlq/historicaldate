# historicaldate

An open source package for creating timelines
of historical data

Download the *historicaldate* package from 
https://github.com/dh3968mlq/historicaldate

Sample code:

```python
# The folder historicaldate has been downloaded to
hdroot = "/svol1/pishare/users/pi/repos/historicaldate" 
import sys
sys.path.append(hdroot)
from historicaldate import hdplotly as hdp
import pandas as pd

df = pd.read_csv(f"{hdroot}/data/history/europe/United Kingdom/British Monarchs.csv", na_filter=False)
df2 = pd.read_csv(f"{hdroot}/data/history/europe/United Kingdom/British Prime Ministers.csv", na_filter=False)

pltl = hdp.plTimeLine()
pltl.add_event_set(df, title="British Monarchs from 1066")
pltl.add_event_set(df2, title="British Prime Ministers") 
pltl.show() 
```

The basic ideas here are:
   * Dates specified in natural formats, allowing for uncertainty, usually in .csv files
   * Can specify start and end of persistent events, such as a US presidency or a British monarch's reign...
   * ... Or a single date for an event
   * Can specify birth and death dates of persons
   * Support for easily displaying timelines of events using *Plotly*...
   * ... which gives basic interactivity: zoom, pan, hovertext and hyperlinks
   * Some useful data files held in the repository
   

## (Old version) Introduction

Standard computer date formats are generally unsuitable for storing dates of historical events, since:
   1. Computer date formats often have an earliest date they can represent, sometimes as recent as 1677 (the earliest date a Pandas timestamp can represent)
   2. Dates of historical events may not be known precisely. Only a month or a year may be known, or a range of possible dates
   3. Dates of historical events are most often quoted in a *calendar* that is itself not fully specified, particularly in distinguishing between the Julian and Gregorian calendars. The usual convention is that a date specified as 'CE' (or, equivalently 'AD') uses the calendar in force at the place of the event at the time, but the switch from the Julian to the Gregorian calendar took place at different times in different countries.

The imprecision in the calendar may be irrelevant for most applications, such as those that do not require precision to within a few days, or that cover a time period only after the Gregorian calendar had come into general use.

The Pandas *period* object class goes some way towards meeting these requirements, but does not deal with all of them.

This all leads to the suggestion that dates of historical events should be stored as **text**, in a way that accepts imprecision in both the date and the calendar. This approach gives the added benefit that dates can then be stored in a format that is familiar to historians or genealogists such as:
   - 25 Dec 1066
   - circa 1483
   - Between 500 BC and 200 AD

## General approach

   1. Historical dates are stored as text, in an intuitive format that allows imprecision (e.g. year only or 'circa') and ranges
   1. A historical date (if CE/AD) is converted to three Python date values (for CE dates): 
   earliest, midpoint and latest, together with indications of
   whether these are *stated*, as opposed to being estimated from 'circa' or as the midpoint of a range
   1. A 'naive' approach to Python dates. 25th December 1066 becomes the Python date 1066-12-25, even though the former, by normal convention,
   is Julian calendar and Python dates represent, strictly speaking, a proleptic (extended backwards in time) Gregorian calendar

## Requirements

The aim here:
   1. To deal with dates in history, CE (AD) or BCE (BC)
   2. To store them, in (e.g.) databases
   3. To allow non-technical users to specify dates in an intuitive way, following usual historical conventions
   4. To deal with uncertainty: e.g. specify a month, or a year or a range
   5. To deal with the difference between Julian and Gregorian calendars in a sensible way, in particular not forcing the user to worry about it it cases when it doesn't matter

The main historical conventions to 
be followed are:
   1. Dates are written in the calendar operating in the region at the time
   2. A new year always starts on 1st January. (i.e. dates are always 'new format')
   3. There should be no requirement to always specify *precisely* what calendar is in operation, since most of the time it doesn't matter

The general approach:
   1. Dates are stored (in, for example, a database of a spreadsheet) as strings, since no existing computer date format meets all requirements.
   2. A calendar is always specified, but will most often be CE or BCE, and these do not completely specify everything about the calendar
   3. This lack of complete specification still allows many approximate operations, such as display on a timeline, or approximate event ordering
   4. In the minority of cases where this lack of precision matters, there can be options to convert dates to a completely specified calendar

## Specification

A date has the following parts, each one optional, in this order if they appear
   1. A **circa specification**
   1. A **central date**
   1. An **earliest date**
   1. A **latest date**

### circa specification

   - Starts with a keyword: one of 'circa', 'c','c.', 'about' or 'estimated'
   - Optionally followed *immediately* (no spaces) with an inication of uncertainty, which can be
      - a number of years (y): e.g. *circa2y* to indicate 2 years' uncertainty
      - a number of months (m): e.g. *circa6m* to indicate 6 months' uncertainty
      - a number of days (d): e.g. *circa10d* to indicate 10 days' uncertainty
   - If no circa specification is given, it defaults to 5 years

The circa specification is used in (only) the following ways:
   1. To estimate earliest date if none is given, from the 
   central date
   1. To estimate latest date if none is given, from the 
   central date
   1. To estimate central and latest dates from earliest date, if earliest date is the only date given
   1. To estimate central and earliest dates from latest date, if latest date is the only date given

### Date specifications

Day and month are optional, year is required

Each date may be written in either prefix or suffix form:

**Prefix form date examples**

The month must be indicated by its name (or the first three
letters), not by a number

   - 25th December 1066
   - 25 dec 1066
   - December 1066 ad
   - 1066 ce

**Suffix form date examples**

The month must be indicated by its number, and the hyphens are required

   - 1066-12-25
   - 1066-12 ad
   - 1066 ce



   
   