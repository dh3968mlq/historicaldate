# historicaldate

A small Python package for date handling including support for BC dates and uncertainty.

It is intended for dealing with historical events. It does not support time of day, and at present takes a naive approach to 
the difference between Julian and Gregorian calendars, since this is usually what is needed for the expected application areas.

The package provides a parser for date formats that are often used to indicate uncertain dates, such as

*   circa 1989
*   between 1920 and 1934
*   2003
*   circa 1483 earliest 1483

The parser converts these to a *HDate()* object, which stores the earliest possible, latest possible and an approximate midpoint date corresponding to the original string. these dates are stored as:

1.  Ordinals. These correspond to Python *datetime* ordinals for AD dates, extended backwards to non-positive values for BC dates.
1.  Python *datetime.date*, for AD dates only.

## Date formats

### Two core formats are supported by default
   * 25 Dec 1066 (or variants such as 25th Dec 1066 or 25 December 1066 etc.)
   * 1066-12-25

### Additional formats are also supported

Specifying ***dateformat="dmy"*** (as a parameter to either the *HDate* constructor ) also allows...
   * 25/12/1066

Specifying ***dateformat="mdy"*** allows...
   * 12/25/1066
   * Dec 25, 1066

But does not allow...
   * 25/12/1066
   * 25 Dec 1066

### The exact date is not required

These are all allowed:
   * Dec 1066
   * 1066
   * 1066-12
   * circa 1066
   * c. 1066
   * between 1066 and 1068
   * circa 1483 earliest 1483

### Ongoing events are supported

A date value of 'ongoing' leads to the earliest and midpoint dates taking
values *datetime.date.today()*, the late date being a few years in
the future, with flags set for 'ongoing'

### The difference between Julian and Gregorian calendars is (as yet) ignored

Python dates are used for AD (CE) timeline displays,
and *25 Dec 1066* converts to the Python date *1066-12-25*.

This gets us into the tricky question of the few days difference between the Julian and Gregorian calendars. The approach here is (at least for the moment) to observe that this difference doesn't have any significant impact on most expected application areas, and so can be ignored.

In effect this package naively assumes that any AD date string passed to *HDate* is (proleptic) Gregorian, the same assumption that is made by Python's *datetime.date*.
This is 'naive' because the usual convention when quoting historical dates is to use the calendar in operation at the relevant place at the time. So when we say that the coronation of William I of England took place on 25 Dec 1066, that is a Julian date, not a proleptic Gregorian date (which I believe would be 31 Dec 1066).

It's expected this approach will continue to be the default, since to do anything else would make things unnecessarily more complex for most applications. It's possible however that Julian / Gregorian conversion functionality may be added to future versions

(*Proleptic Gregorian Calendar*: A Gregorian calendar extended backwards in time before the dates, starting in the 16th century AD, that the Gregorian calendar was actually introduced)

# Dealing with dates - the HDate() class

Objects of this class have a property *pdates*, a dictionary encoding the date information.

### Examples

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

These are usual Python date ordinals (int) for AD dates as created by *datetime.date.toordinal()*, extended backwards in time to non-positive numbers for BC dates assuming that 1BC, 5BC etc. are leap years. See above for how the few days difference between the Julian and Gregorian calendars is treated.

AD dates are also given values of *early*, *mid* and *late*, which are the equivalent Python dates (*datetime.date* objects).

The dictionary members *slearly*, *slmid* and *sllate* indicate the 'specification level' of the corresponding date, and take the following values:

| Value | Meaning |
| ------ | ----- |
| 'd'   | day  |
| 'm'   | month  |
| 'y'   | year  |
| 'c'   | Derived from a 'circa' calculation  |
| 'o'   | Derived from an 'ongoing' calculation  |


## Constructor

*hd = hdate.HDate(hdstr="", missingasongoing=False, dateformat=None)*

| Parameter | Usage |
| ------ | ----- |
| hdstr : str   | String indicating the date. See description above for allowed date formats  |
| missingasongoing: bool | Indicates if a null string is to be interpreted as indicating 'ongoing' or (equivalently) 'alive' |
| dateformat : str | If *None*, date formats accepted are variants of *25 Dec 1066* and *1066-12-25*. If *dateformat='dmy'* then *25/12/1066* is also accepted. If *dateformat='mdy'* then *12/25/1066*, *Dec 25 1066* and *1066-12-25* are accepted, but *25 Dec 1066* is not accepted |


## *hdate* utility functions

In all *hdate* utility functions 
   * The parameter *date_or_ordinal* may be passed as either a Python date (datetime.date), an ordinal (int) (which may be less than zero) or as a date string (str) in a format acceptable to HDate.
   * The parameter *dateformat* is equivalent to the same parameter in the *HDate* constructor. See above for details.

### *ord = to_ordinal(date_or_ordinal, delta=0, dateformat=None)*

Converts a date or ordinal value to an ordinal. 

*delta*: indicates a number of days to be added to the original date.

### *pdate = to_python_date(date_or_ordinal, dateformat=None)*

Converts a date or ordinal value to a python date. 

Returns a *None* value if *date_or_ordinal* is BC.

### *yrs = to_years(date_or_ordinal, dateformat=None)*

Converts a date or ordinal to an approximate number of years (float). The returned value 0.0 corresponds to ordinal value 0, which is 31st December, 1BC.

The implementation is approximate, but believed to be good enough for most timeline displays.

### *syear = format_year(year, showzeroas1ad=True, adtext="AD", bctext="BC")*

Formats a year (int or float) in a way suitable for display on an X-axis that is showing dates as float values corresponding to years.

### *ord = years_to_ordinal(years)*

Converts a year number (float) to an ordinal.

Also approximate, but an exact inverse of *to_years*

### *ymd = to_ymd(date_or_ordinal, dateformat=None)*

Converts a date or ordinal to a named tuple containing year, month and day numbers

The tuple definition is:
```python
YMD = namedtuple("YMD", "year month day")
```

### *ord = calc_mid_ordinal(hdstring, dateformat=None)*

Returns the mid-point ordinal from a date held as a string in *HDate* format


## Changes

### New in 0.0.7

The package has been trimmed down to date treatment only.
The Plotly utilities included in older versions are now at
https://github.com/dh3968mlq/hdtimelines

### New in 0.0.6

*add_event_set* renamed to *add_topic_from_df*

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
   