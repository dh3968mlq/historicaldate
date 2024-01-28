# historicaldate

A small Python package for date handling including support for BC dates and uncertainty.

```text
$ pip install historicaldate
```

PyPI: https://pypi.org/project/historicaldate/

Documentation: https://historicaldate.readthedocs.io/en/stable/

The package provides a parser for date formats that are often used
to indicate uncertain dates, such as

*   circa 1989
*   between 1920 and 1934
*   2003
*   circa 1483 earliest 1483

These string are converted to a *HDate()* object, which stores the earliest,
latest possible and an approximate midpoint date corresponding to the 
original string. These dates are stored as:

1.  Ordinals. These correspond to Python *datetime* ordinals for AD dates, extended backwards to non-positive values for BC dates.
1.  Python *datetime.date*, for AD dates only.

The package is intended for dealing with historical events. It does not support time of day,
and at present takes a naive approach to 
the difference between Julian and Gregorian calendars since 
this is usually what is needed for the expected application areas.

## Date formats

### Two core formats are supported by default
   * 25 Dec 1066 (or variants such as 25th Dec 1066 or 25 December 1066 etc.)
   * 1066-12-25

### Additional formats are also supported

Specifying ***dateformat="dmy"*** (as a parameter to the *HDate* constructor ) also allows...
   * 25/12/1066

Specifying ***dateformat="mdy"*** allows...
   * 12/25/1066
   * Dec 25, 1066
   * 1066-12-25

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
>>>
>>>hd2 = hdate.HDate('Dec 20, 1066', dateformat="mdy")
>>>print(hd2.pdates)
{'mid': datetime.date(1066, 12, 20), 'ordinal_mid': 389337, 'slmid': 'd',
 'late': datetime.date(1066, 12, 20), 'ordinal_late': 389337, 'sllate': 'd',
 'early': datetime.date(1066, 12, 20), 'ordinal_early': 389337, 'slearly': 'd'}
>>>
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

## Changes

### New in 0.1.0, 0.1.1, 0.1.2

Cleaned up for PyPI release

### New in 0.0.7

The package has been trimmed down to date treatment only.
The Plotly utilities included in older versions are now at
https://github.com/dh3968mlq/hdtimelines

### New in 0.0.5

   * BC dates are now supported
   * Ordinal dates implemented
   * *dateformat* implemented, allowing dates to be formatted as *25/12/1066* or *12/25/1066* or *Dec 25, 1066*
   
   