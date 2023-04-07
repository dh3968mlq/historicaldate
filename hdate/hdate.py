'''
Object class to deal with historical dates, stored as strings
'''

import re
import datetime

class HDate():
    def __init__(self, hdstr=""):
        self.match_pattern = self._create_match_pattern()
        self.compiled_pattern = re.compile(self.match_pattern, re.IGNORECASE)
        srch = self.compiled_pattern.search(hdstr)
        if srch is None:
            raise ValueError("Illegal date format")
        else:
            self.re_parsed = {key:srch[key] for key in self.compiled_pattern.groupindex}

        self.d_parsed = self._convert_re_parsed()

    def _create_match_pattern(self):
        circa_pattern = "circa|c|c.|about|estimated"
        day_pattern = "[0-9]{1,2}"

        months = ["january", "february","march","april","may","june",
                "july","august","september","october","november","december"]
        self.months = [month[0:3] for month in months]   # three-letter abbreviations 
        month_pattern = "|".join(months + self.months)   # allow either full month names or 3-letter abbrevations
        year_pattern = "[0-9]{3,8}"    # require at least three year digits to avoid confusion with month and day
        nmonth_pattern = "[0-9]{1,2}"
        calendar_pattern = "ce|ad|bc|bce"

        def makedatepattern(prefix=""):
            datepattern = f"((?P<{prefix}preday>{day_pattern})?" \
                    f"\\s*(?P<{prefix}premon>{month_pattern}))?" \
                    f"\\s*(?P<{prefix}year>{year_pattern})" +  \
                    f"(-(?P<{prefix}postmon>{nmonth_pattern})" + \
                    f"(-(?P<{prefix}postday>{day_pattern}))?)?"
            return datepattern

        pattern = f"^(?P<circa>{circa_pattern}\\s)?" + \
                f"\\s*" + makedatepattern() + \
                f"(\\s+(earliest|after)\\s+" + makedatepattern(prefix="early") + ")?" + \
                f"(\\s+(latest|before)\\s+" + makedatepattern(prefix="late") + ")?" + \
                f"(\\s+(?P<calendar>{calendar_pattern}))?" + \
                "$"  

        return pattern

    def _convert_re_parsed(self):
        "Convert re_parsed format to d_parsed format"

        sp = self.re_parsed

        # preday and postday cannot both be set, ditto premon and postmon
        if sp["premon"] is not None and sp["postmon"] is not None:
            raise ValueError("Prefix month and postfix month cannot both be set")
        if sp["earlypremon"] is not None and sp["earlypostmon"] is not None:
            raise ValueError("Earliest ('after') prefix month and postfix month cannot both be set")
        if sp["latepremon"] is not None and sp["latepostmon"] is not None:
            raise ValueError("Latest ('before') prefix month and postfix month cannot both be set")
        
        # Failing here should be impossible if tests above are passed
        assert sp["preday"] is None or sp["postday"] is None
        assert sp["earlypreday"] is None or sp["earlypostday"] is None
        assert sp["latepreday"] is None or sp["latepostday"] is None

        hd = {}
        hd["circa"] = sp["circa"] is not None  # 'circa':bool

        def getmonthnum(month):
            return self.months.index(month[0:3].lower()) + 1

        def set_dmy(prefix=""):
            """
            To do: check values are within range
            """
            hd[prefix+"day"] = int(sp[prefix+"preday"]) if sp[prefix+"preday"] is not None \
                        else int(sp[prefix+"postday"]) if sp[prefix+"postday"] is not None \
                        else None
            hd[prefix+"mon"] = getmonthnum(sp[prefix+"premon"]) if sp[prefix+"premon"] is not None \
                        else int(sp[prefix+"postmon"]) if sp[prefix+"postmon"] is not None \
                        else None
            hd[prefix+"year"] = int(sp[prefix+"year"]) if sp[prefix+"year"] is not None \
                        else None

        set_dmy()
        set_dmy("early")
        set_dmy("late")
        hd["calendar"] = sp["calendar"].lower() if sp["calendar"] is not None else "ce"
        return hd
    
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
        # function to convert a date
        def convert_one_date(prefix=""):
            if self.d_parsed[f'{prefix}year'] is None:
                return None
            else:
                return datetime.date(self.d_parsed[f'{prefix}year'], 
                           self.d_parsed[f'{prefix}mon'] if self.d_parsed[f'{prefix}mon'] is not None else 6,
                           self.d_parsed[f'{prefix}day'] if self.d_parsed[f'{prefix}day'] is not None else 15)
        
        # -- convert the core date, if it exists
        #self.naive_python_date = datetime.date(self.d_parsed['year'], 
        #                   self.d_parsed['mon'] if self.d_parsed['mon'] is not None else 6,
        #                   self.d_parsed['day'] if self.d_parsed['day'] is not None else 15)
        self.naive_python_date = convert_one_date()
        self.naive_python_latedate = convert_one_date("late")
        self.naive_python_earlydate = convert_one_date("early")
        ...
