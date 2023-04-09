# historydate

## Introduction

Standard computer date formats are generally unsuitable for storing dates of historical events, because:
   1. Computer date formats often have an earliest date they can represent, sometimes as recent as 1677 (the earliest date a Pandas timestamp cen represent)
   2. Dates of historical events may not be known precisely. Only a month or a year may be known, or a range of possible dates
   3. Dates of historical events are most often quoted in a *calendar* that is itself not fully specified, particularly in distinguishing between the Julian and Gregorian calendars. The usual convention is that a date specified as 'CE' (or, equivalently 'AD') uses the calendar in force at the place of the event at the time, but the switch from the Julian to the Gregorian calendar took place at different times in different countries.

The imprecision in the calendar may be irrelevant for most applications, such as those that do not require precision to within a few days, or that cover a time period only after the Gregorian calendar had come into general use.

The Pandas *period* object class goes some way towards meeting these requirements, but does not deal with all of them.

This all leads to the suggestion that dates of historical events should be stored in, for example, databases or spreadsheets as **text**, in a way that accepts imprecision in both the date and the calendar. This approach gives the added benefit that dates can then be stored in a format that is familiar to historians or genealogists such as:
   - 25 Dec 1066
   - circa 1483
   - Between 500 BC and 200 AD

The approach here is to specify allowed formats that includes the examples above, and can also be interpreted as indicating a range of dates.

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
