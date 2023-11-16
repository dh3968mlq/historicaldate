import datetime
from collections import namedtuple

try:
    import historicaldate.hdate as hdate
except:
    import historicaldate.historicaldate.hdate as hdate


def to_ordinal(date_or_ordinal, delta=0, dateformat=None):
    "Takes either a python date, an (int) ordinal or a string, returns an ordinal. Optionally apply a delta (days)"
    if date_or_ordinal is None:
        return None
    elif type(date_or_ordinal) == datetime.date:
        return date_or_ordinal.toordinal() + delta
    elif type(date_or_ordinal) == int:
        return date_or_ordinal + delta
    elif type(date_or_ordinal) == str:
        return hdate.HDate(date_or_ordinal, dateformat=dateformat).pdates["ordinal_mid"]
    else:
        raise TypeError(f"date_or_ordinal must be int or datetime.date or str, not {type(date_or_ordinal)}")
# ----
def to_python_date(date_or_ordinal, dateformat=None):
    """
    Takes either a python date or an (int) ordinal.
    Returns a Python date if ordinal >= 1, None otherwise.
    """
    if date_or_ordinal is None:
        return None
    elif type(date_or_ordinal) == datetime.date:
        return date_or_ordinal
    elif type(date_or_ordinal) == int:
        return datetime.date.fromordinal(date_or_ordinal) if date_or_ordinal >= 1 else None
    elif type(date_or_ordinal) == str:
        return hdate.HDate(date_or_ordinal, dateformat=dateformat).pdates["ordinal_mid"]
    else:
        raise TypeError(f"date_or_ordinal must be int or datetime.date or str, not {type(date_or_ordinal)}")
# ----
def to_years(date_or_ordinal, dateformat=None):
    """
    Takes either a python date or an (int) ordinal, returns an number of years (float).
    Years is continuous, with 0.0 corresponding to ordinal day 0, i.e. 31st December 1BC
    """
    if pdate := to_python_date(date_or_ordinal):
        daynum = pdate.toordinal() - datetime.date(pdate.year,1,1).toordinal() + 1
        daysinyear = datetime.date(pdate.year,12,31).toordinal() - datetime.date(pdate.year,1,1).toordinal() + 1
        years = float(pdate.year) - 1 + daynum / daysinyear
        return years
    elif (odate := to_ordinal(date_or_ordinal, dateformat=dateformat)) is not None:   # BC
        years = odate / 365.2425                    # Sloppy, but good enough for most applications
    else:
        years = None
    return years
# ----
def format_year(year, showzeroas1ad=True, adtext="AD", bctext="BC"):
    iyear = int(year)
    if iyear > 0 or (iyear == 0 and not showzeroas1ad):
        syear = f"{iyear:04d}"
    elif iyear == 0:
        syear = f"1{adtext}"
    else:
        syear = f"{abs(iyear)}{bctext}"
    return syear

# ----
def years_to_ordinal(years):
    return int(years * 365.2425)           # Just as sloppy, but good enough for its only application to date
# ----
def to_ymd(date_or_ordinal, dateformat=None):
    YMD = namedtuple("YMD", "year month day")
    if pdate := to_python_date(date_or_ordinal):
        ymd = YMD(pdate.year, pdate.month, pdate.day)
    elif (odate := to_ordinal(date_or_ordinal, dateformat=dateformat)) is not None:  
        days_in_4years_julian = 3*365 + 366
        cycles = (odate - 1) // days_in_4years_julian           # cycles < 0
        ad_ordinal = odate - cycles * days_in_4years_julian # Shift it forward by a multiple of 4 years to positive number
        assert ad_ordinal > 0

        ad_date = datetime.date.fromordinal(ad_ordinal)
        ymd = YMD(ad_date.year + 4*cycles - 1, ad_date.month, ad_date.day) # Adjust year, there is no year 0
    else:
        ymd = None
    return ymd
# ----
def calc_mid_ordinal(hdstring, dateformat=None):
    "Return the mid date from an hdate string, or None"
    try:
        hd = hdate.HDate(hdstring, dateformat=dateformat)
        return hd.pdates['ordinal_mid']
    except:
        return None
