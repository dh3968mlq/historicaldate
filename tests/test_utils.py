import sys
import random

sys.path.append(".")

import historicaldate.hdate as hdate
import historicaldate.hdateutils as hdateutils

def check_ordinal(ordinal):
    "Cycle ordinal -> ymd -> string -> ordinal"
    months = ["Jan", "Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    ymd = hdateutils.to_ymd(ordinal)
    s = f"{ymd.day} {months[ymd.month - 1]} {abs(ymd.year)}"
    if ymd.year < 0:
        s = s + " BCE"
    hd = hdate.HDate(s)
    ord2 = hdateutils.to_ordinal(hd.pdates["ordinal_mid"])
    assert ordinal == ord2, f"cycle1 failed on input ordinal {ordinal}: ymd={ymd}, s='{s}', ord2={ord2}"

def cycle1(ntries, lo=-365*2500, hi=365*2500):
    "Cycle ordinal -> ymd -> string -> ordinal for ntries random ordinals"
    months = ["Jan", "Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for _ in range(ntries):
        ordinal = random.randint(lo, hi)
        check_ordinal(ordinal)

def test1():
    cycle1(5000)

def test2():
    "Single try, put problem cases here for debugging"
    check_ordinal(-515733)