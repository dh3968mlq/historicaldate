'''
Object class to deal with historical dates, stored as strings
'''

import re

class HDate():
    def __init__(self, hdstr=""):
        self.match_pattern = create_match_pattern()
        self.compiled_pattern = re.compile(self.match_pattern, re.IGNORECASE)
        srch = self.compiled_pattern.search(hdstr)
        if srch is None:
            raise ValueError("Illegal date format")
        else:
            self.parsed = {key:srch[key] for key in self.compiled_pattern.groupindex}

def create_match_pattern():
    circa_pattern = "circa|c|c.|about|estimated"
    day_pattern = "[0-9]{1,2}"

    months = ["january", "february","march","april","may","june",
            "july","august","september","october","november","december"]
    month_pattern = "|".join(months + [month[0:3] for month in months])
    year_pattern = "[0-9]{1,4}"
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
