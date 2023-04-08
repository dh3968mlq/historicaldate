## historydate
Treatment of historical dates

The aim here:
   1. To deal with dates in history, CE (AD) or BCE (BC)
   2. To store them, in (e.g.) databases
   3. To allow non-technical users to specify dates in an intuitive way, following usual historical conventions
   4. To deal with uncertainty: e.g. specify a month, or a year or a range
   5. To deal with the difference between Julian and Gregorian calendars in a sensible way

The main historical conventions to 
be followed are:
   1. Dates are written in the calendar operating in the region at the time
   2. ... except that a new year always starts on 1st January. (i.e. dates are always 'new format')
   3. There should be no requirement to always specify *precisely* what calendar is in operation, since most of the time it doesn't matter

The general approach:
   1. Dates are stored (in, for example, a database of a spreadsheet) as strings, since no existing computer date format meets all requirements.
   2. A calendar is always specified, but will most often be CE or BCE, and these do not completely specify everything about the calendar
   3. This lack of complete specification still allows many approximate operations, such as display on a timeline, or approximate event ordering
   4. In the minority of cases where this lack of precision matters, there can be options to convert dates to a completely specified calendar
