'''
    Handling dates of historical events and timelines
    Copyright (C) 2023  David Harris

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    License at https://github.com/dh3968mlq/historicaldate/blob/main/LICENSE
'''

import re
import datetime
from collections import namedtuple

# -- Some utilities
def to_ordinal(date, delta=0):
    "Takes either a python date, an (int) ordinal or a string, returns an ordinal. Optionally apply a delta (days)"
    if date is None:
        return None
    elif type(date) == datetime.date:
        return date.toordinal() + delta
    elif type(date) == int:
        return date + delta
    elif type(date) == str:
        return HDate(date).pdates["ordinal_mid"]
    else:
        raise TypeError(f"date must be int or datetime.date, not {type(date)}")
# ----
def to_python_date(ordinal):
    """
    Takes either a python date or an (int) ordinal.
    Returns a Python date if ordinal >= 1, None otherwise.
    """
    if ordinal is None:
        return None
    elif type(ordinal) == datetime.date:
        return ordinal
    elif type(ordinal) == int:
        return datetime.date.fromordinal(ordinal) if ordinal >= 1 else None
    else:
        raise TypeError(f"ordinal must be int or datetime.date, not {type(ordinal)}")

def to_years(date_or_ordinal):
    """
    Takes either a python date or an (int) ordinal, returns an number of years (float).
    Years is continuous, with 0.0 corresponding to ordinal day 0, i.e. 31st December 1BC
    """
    if pdate := to_python_date(date_or_ordinal):
        daynum = pdate.toordinal() - datetime.date(pdate.year,1,1).toordinal() + 1
        daysinyear = datetime.date(pdate.year,12,31).toordinal() - datetime.date(pdate.year,1,1).toordinal() + 1
        years = float(pdate.year) - 1 + daynum / daysinyear
        return years
    elif (odate := to_ordinal(date_or_ordinal)) is not None:   # BC
        years = odate / 365.25                    # Sloppy, but good enough for most applications
    else:
        years = None
    return years
# ----
def years_to_ordinal(years):
    return int(years * 365.25)           # Just as sloppy, but good enough for its only application to date
# ----
def to_ymd(date_or_ordinal):
    YMD = namedtuple("YMD", "year month day")
    if pdate := to_python_date(date_or_ordinal):
        ymd = YMD(pdate.year, pdate.month, pdate.day)
    elif (odate := to_ordinal(date_or_ordinal)) is not None:   # BC
        days_in_4years_julian = 3*365 + 366
        cycles = odate // days_in_4years_julian           # cycles < 0
        ad_ordinal = odate - cycles * days_in_4years_julian # Shift it forward by a multiple of 4 years to positive number
        assert ad_ordinal > 0

        ad_date = datetime.date.fromordinal(ad_ordinal)
        ymd = YMD(ad_date.year + 4*cycles - 1, ad_date.month, ad_date.day) # Adjust year, there is no year 0
    else:
        ymd = None
    return ymd
# ----
def calc_mid_ordinal(hdstring):
    "Return the mid date from an hdate string, or None"
    try:
        hd = HDate(hdstring)
        return hd.pdates['ordinal_mid']
    except:
        return None
# ------------------------------------------------------------------------------------------------------
class HDate():
    """
    Object class to deal with historical dates, stored as strings
    See README.md at https://github.com/dh3968mlq/historicaldate
    """
    def __init__(self, hdstr="", missingasongoing=False, prefixdateorder=None):
        self.circa_interval_days = int(5 * 365.25)
        self.match_pattern = self._create_match_pattern(prefixdateorder)
        self.compiled_pattern = re.compile(self.match_pattern, re.VERBOSE | re.IGNORECASE)

        if s := (hdstr.strip() if (hdstr.strip() or not missingasongoing) else "ongoing"):
            srch = self.compiled_pattern.search(s)
            if srch is None:
                raise ValueError(f"Illegal date format: {hdstr}")
            else:
                self.re_parsed = {key:srch[key] for key in self.compiled_pattern.groupindex}

            self.d_parsed = self._convert_re_parsed()
        else:
            self.d_parsed = None

        try:
            self.convert_to_python_date_naive()
        except:
            self.pdates = None
            
    # ------------------------------------------------------------------------------------------------------
    def _create_match_pattern(self, prefixdateorder):
        circa_pattern = "circa|c|c.|about|estimated"
        day_pattern = "[0-9]{1,2}"

        months = ["january", "february","march","april","may","june",
                "july","august","september","october","november","december"]
        self.months = [month[0:3] for month in months]   # three-letter abbreviations 
        self.monthnumberpattern = '[1-9]|0[1-9]|1[0-2]'
        month_pattern = "|".join(months + self.months)   # allow either full month names or 3-letter abbrevations

        if prefixdateorder:   # if not None then numerical months are also allowed
            month_pattern += "|" + self.monthnumberpattern

        year_pattern = "[0-9]{1,8}"    # should we require at least three year digits to avoid confusion with month and day?
        nmonth_pattern = "[0-9]{1,2}"
        calendar_pattern = "ce|ad|bc|bce"

        def makedatepattern(prefix=""):
            if prefixdateorder is None or prefixdateorder.lower() == "dmy":
                datepattern = f"""
                    (
                        (
                            (?P<{prefix}preday>{day_pattern})(st|nd|rd|th)?)?
                            \\s*/?\\s*(?P<{prefix}premon>{month_pattern})(,)?
                        )?
                        \\s*/?\\s*(?P<{prefix}year>{year_pattern})
                        (-(?P<{prefix}postmon>{nmonth_pattern})
                            (-(?P<{prefix}postday>{day_pattern})
                            )?
                        )?
                        (\\s+(?P<{prefix}calendar>{calendar_pattern}))?
                """
            elif prefixdateorder.lower() == "mdy":
                datepattern = f"""
                    (
                        (
                            (?P<{prefix}premon>{month_pattern})
                            \\s*/?\\s*(?P<{prefix}preday>{day_pattern})(st|nd|rd|th)?)?
                            (,)?
                        )?
                        \\s*/?\\s*(?P<{prefix}year>{year_pattern})
                        (-(?P<{prefix}postmon>{nmonth_pattern})
                            (-(?P<{prefix}postday>{day_pattern})
                            )?
                        )?
                        (\\s+(?P<{prefix}calendar>{calendar_pattern}))?
                """
            else:
                raise NotImplementedError(f"prefixdateorder must be None, 'dmy' or 'mdy': not '{prefixdateorder}'")
            return datepattern

        pattern = f"""
                ^(
                    (?P<ongoing>ongoing)|
                    ((?P<circa>{circa_pattern})
                        ((?P<clen>{year_pattern})
                            (?P<clentype>y|m|d)
                        )?
                    )?
                    (\\s*{makedatepattern(prefix="mid")})?
                    (\\s*(earliest|after|between)\\s+{makedatepattern(prefix="early")})?
                    (\\s*(latest|before|and)\\s+{makedatepattern(prefix="late")})?
                )$
        """  

        return pattern
    # ------------------------------------------------------------------------------------------------------
    def _convert_re_parsed(self):
        """
        Convert re_parsed format to d_parsed format
        This represents canonical form, so
           - Represents Y/M/D as integers
           - Does no calculations
           - converts calendars to bce or ce
           - sets main calendar, others are set only if different
        """

        sp = self.re_parsed

        # preday and postday cannot both be set, ditto premon and postmon
        def check_prepost_dup(prefix):
            if sp[f"{prefix}premon"] is not None and sp[f"{prefix}postmon"] is not None:
                raise ValueError(f"Prefix month and postfix month ({prefix}) cannot both be set")
            # Failing here should be impossible if test above is passed
            assert sp[f"{prefix}preday"] is None or sp[f"{prefix}postday"] is None

        check_prepost_dup("mid")
        check_prepost_dup("early")
        check_prepost_dup("late")

        hd = {}
        hd["circa"] = sp["circa"] is not None  # 'circa':bool
        hd["ongoing"] = sp["ongoing"] is not None  # 'ongoing':bool
        hd["clen"] = sp["clen"]
        hd["clentype"] = sp["clentype"]

        def getmonthnum(month):
            if len(month) >= 3 and month[0:3].lower() in self.months:
                monthnum = self.months.index(month[0:3].lower()) + 1
            elif re.search(self.monthnumberpattern, month):
                monthnum = int(month)
            else:
                assert False, f"Illegal month string {month}"
            assert monthnum >= 1 and monthnum <= 12
            return monthnum
                            
        def set_dmy(prefix=""):
            """
            To do: check values are within range???
            """
            hd[prefix+"day"] = int(sp[prefix+"preday"]) if sp[prefix+"preday"]  \
                        else int(sp[prefix+"postday"]) if sp[prefix+"postday"]  \
                        else None
            hd[prefix+"mon"] = getmonthnum(sp[prefix+"premon"]) if sp[prefix+"premon"]  \
                        else int(sp[prefix+"postmon"]) if sp[prefix+"postmon"]  \
                        else None
            hd[prefix+"year"] = int(sp[prefix+"year"]) if sp[prefix+"year"] else None
            ctemp = sp[prefix+"calendar"].lower() if sp[prefix+"calendar"] else None
            hd[prefix+"calendar"] = {'bc':'bce','ad':'ce'}.get(ctemp, ctemp)

        set_dmy("mid")
        set_dmy("early")
        set_dmy("late")

        # resolve calendars
        # (1) if main is missing, copy from late
        # (2) if main is still missing, and early is ad/ce, copy from early (else error)
        # (3) if early / late is same as main, set to none
        if hd["midcalendar"] is None: hd["midcalendar"] = hd["latecalendar"]
        if hd["midcalendar"] is None: 
            if hd["earlycalendar"] is None:
                pass
            elif hd["earlycalendar"].lower() in  {'bc', 'bce'}:
                raise ValueError("If early calendar is BC/BCE, main calendar must be specified")
            else:
                hd["midcalendar"] = hd["earlycalendar"]
        
        if hd["latecalendar"] == hd["midcalendar"]: hd["latecalendar"] = None
        if hd["earlycalendar"] == hd["midcalendar"]: hd["earlycalendar"] = None

        return hd
    # ------------------------------------------------------------------------------------------------------
    def max_day_in_month(self,year, month, proleptic_gregorian=False, calendar='ce'):
        '''
        month has range 1-12

        If proleptic is False: Assumes possible Julian calendar to 1752, Gregorian after that
        So max_day_in_month(1700, 2) == 29
        So max_day_in_month(1800, 2) == 28

        If proleptic is True: Assumes Gregorian calendar throughout
        So max_day_in_month(1700, 2) == 28

        If a Julian calendar is used, a proleptic Julian calendar is used before 8AD, when leap years
        every four years became standardised. So in both systems the years 4AD, 1BC, 5BC etc. are
        treated as leap years
        '''
        mlengths = [31,28,31,30,31,30,31,31,30,31,30,31]
        mlength = mlengths[month-1]

        if month != 2:
            pass    # no further adjustment needed
        elif calendar.lower() in {'ce','ad'}:
            grg_nonleap = (year % 100 == 0) and (year % 400 != 0)
            isleapyear = (year % 4 == 0) and not (grg_nonleap and (year > 1752 or proleptic_gregorian))
            mlength = 29 if isleapyear else 28
        elif calendar.lower() in {'bce','bc'}:  # assume proleptic julian calendar. 1BC, 5BC etc are leap years
            isleapyear = (year % 4 == 1)
            mlength = 29 if isleapyear else 28
        else:
            raise ValueError(f"Calendar must me one of 'ce','ad','bce','bc'")

        return mlength
    # ------------------------------------------------------------------------------------------------------
    def calc_clen_interval(self):
        if not self.d_parsed["clen"]:
            return datetime.timedelta(days=self.circa_interval_days)
        else:
            clen = int(self.d_parsed["clen"])
            if self.d_parsed["clentype"] == "d":
                days = clen
            elif self.d_parsed["clentype"] == "m":
                days = int(clen * 365.25/12)
            elif self.d_parsed["clentype"] == "y":
                days = int(clen * 365.25)
            else:
                raise ValueError
            
            return datetime.timedelta(days=days)
    # ------------------------------------------------------------------------------------------------------
    def _ymd_to_dfragment(self, year, month, day, prefix="mid", speclevel="", isbce=False):
        if isbce: # BC (BCE)
            pythondate = None
            if year % 4 == 1:  # These are the years treated as BC leap years 1, 5, etc.
                ordinal_4ad = to_ordinal(datetime.date(4, month, day))
                nleapdays = (year + 3) // 4 
                ordinal = ordinal_4ad - 365 * (year + 3) - nleapdays
            else:
                ordinal_1ad = to_ordinal(datetime.date(1, month, day))
                nleapdays = (year + 3) // 4 
                ordinal = ordinal_1ad - 365 * year - nleapdays
        else: # AD (CE)
            pythondate = datetime.date(year, month, day)
            ordinal = to_ordinal(pythondate)
        return  {prefix:pythondate, 
                 f"ordinal_{prefix}":ordinal,
                 f"sl{prefix}":speclevel}
    # ------------------------------------------------------------------------------------------------------
    def _convert_one_date(self, prefix=""):
        'Convert a date drawing on self.d_parsed. Also returns indicator of y/m/d specification'
        assert prefix in {"early","mid","late"}
        default_month = 1 if prefix == "early" else 12 if prefix == "late" else 6
        def default_day(year, month):
            return 1 if prefix=="early" \
                        else self.max_day_in_month(year, month) if prefix=="late" \
                        else 15

        isbce = self.d_parsed['midcalendar'] == 'bce'

        if self.d_parsed[f'{prefix}year'] is None:
            if self.d_parsed["circa"] or (prefix == "mid") or \
                        (self.d_parsed[f'midyear'] is None): # Cannot copy from mid year
                return {prefix:None, f"ordinal_{prefix}":None ,f"sl{prefix}":""} 
            else:                # Copy from mid year
                speclevel = self.pdates['slmid']
                year = self.d_parsed[f'midyear']
                month = self.d_parsed[f'midmon'] if speclevel in {"m","d"} else default_month
                day = self.d_parsed[f'midday'] if speclevel == "d" else default_day(year, month)
                return  self._ymd_to_dfragment(year, month, day, prefix=prefix, speclevel=speclevel, isbce=isbce)
        else:    # The date has been specified
            speclevel = "y"
            year = self.d_parsed[f'{prefix}year']

            if self.d_parsed[f'{prefix}mon']: speclevel = "m"
            month = self.d_parsed[f'{prefix}mon'] if speclevel == "m" else default_month
            
            if self.d_parsed[f'{prefix}day']: speclevel = "d"
            day = self.d_parsed[f'{prefix}day'] if speclevel == "d" else default_day(year, month)

            if (self.d_parsed['circa']) and (prefix == "mid"): speclevel = 'c'
            return self._ymd_to_dfragment(year, month, day, prefix=prefix, speclevel=speclevel, isbce=isbce)
    # ------------------------------------------------------------------------------------------------------
    def convert_to_python_date_naive(self):
        """
        date.MINYEAR == 1, so this can only be used for ce (AD) dates
        
        This takes a naive approach to converting to a Python date.
        Python dates use a proleptic Gregorian calendar, (i.e. a Gregorian calendar
        extended back in time to dates when the Gregorian calendar was not used) while our 
        ce dates in principle use the calendar in use in the region at that time. 
        The naive approach used in this method tramples over this distinction, and just converts the
        date to the 'same' Python date. 25 Dec 1066 (Julian) becomes 25 Dec 1066 (proleptic Gregorian),
        not the theoretically correct Gregorian date of 31st Dec 1066

        Because... this is always what a user will want if they are about to display it on a timeline,
        or pretty much anything else for that matter.

        If a date like 29 Feb 300, which existed in Julian calendars but does not
        exist in the proleptic Gregorian calendar, turns up then it is converted to
        28th Feb in the same year
        """            

        if self.d_parsed['ongoing']:
            self.pdates = {'mid': datetime.date.today(), 
                           'ordinal_mid': to_ordinal(datetime.date.today()), 
                           'slmid': 'o', 'slearly': 'o', 'sllate': 'o'}
            self.pdates.update(
                {'late': self.pdates['mid'] + datetime.timedelta(days=self.circa_interval_days),
                 'ordinal_late': self.pdates['ordinal_mid'] + self.circa_interval_days, 
                 'early': self.pdates['mid'],
                 'ordinal_early': self.pdates['ordinal_mid']
                 })
        else:     # Normal treatment, not ongoing
            # -- convert the three dates
            self.pdates = self._convert_one_date("mid") 
            self.pdates.update(self._convert_one_date("late"))
            self.pdates.update(self._convert_one_date("early"))

            # -- Fill early and late dates if missing from (a) circa (b) main date
            circa_interval = self.calc_clen_interval()
            if self.pdates['slmid'] and not self.pdates['slearly']:
                if self.pdates['mid'] and self.pdates['mid'].toordinal() > circa_interval.days:
                    self.pdates.update({'early':self.pdates['mid'] - circa_interval})
                self.pdates.update({'ordinal_early':self.pdates['ordinal_mid'] - circa_interval.days,
                                    'slearly':'c'})
                
            if self.pdates['slmid'] and not self.pdates['sllate']:
                if self.pdates['mid']:
                    self.pdates.update({'late':self.pdates['mid'] + circa_interval})
                self.pdates.update({'ordinal_late':self.pdates['ordinal_mid'] + circa_interval.days,
                                    'sllate':'c'})
                    
            # -- Fill in midpoint date if it is missing and both early and late dates are present
            if self.pdates['slearly'] and self.pdates['sllate'] and not self.pdates['slmid']:
                if self.pdates['early'] and self.pdates['late']:
                    self.pdates.update({'mid':self.pdates['early'] + 
                                            (self.pdates['late'] - self.pdates['early'])/2.0})
                self.pdates.update({'ordinal_mid':(self.pdates['ordinal_early'] + self.pdates['ordinal_late'])//2,
                                    'slmid':'c'})

            # -- Fill in mid and late dates from circa if early is the only date specified
            if self.pdates['slearly'] and not self.pdates['sllate'] and not self.pdates['slmid']:
                if self.pdates['early']:
                    self.pdates.update({'mid':self.pdates['early'] + circa_interval,
                                        'late':self.pdates['early'] + 2 * circa_interval
                                        })
                self.pdates.update({'ordinal_mid':self.pdates['ordinal_early'] + circa_interval.days,
                                    'slmid':'c',
                                    'ordinal_late':self.pdates['ordinal_early'] + 2*circa_interval.days,
                                    'sllate':'c'})

            # -- Fill in mid and early dates from circa if late is the only date specified
            if not self.pdates['slearly'] and self.pdates['sllate'] and not self.pdates['slmid']:
                if self.pdates['late'] and self.pdates['late'].toordinal() > 2 * circa_interval.days:
                    self.pdates.update({'mid':self.pdates['late'] - circa_interval,
                                        'early':self.pdates['late'] - 2 * circa_interval
                                        })
                self.pdates.update({'ordinal_mid':self.pdates['ordinal_late'] - circa_interval.days,
                                'slmid':'c',
                                'ordinal_early':self.pdates['ordinal_late'] - 2 * circa_interval.days,
                                'slearly':'c'})

        # >> to do: deal with dates out of range, 29th feb 1100 etc.
        ...
