import sys
import random

sys.path.append(".")

try:
    import historicaldate.hdate as hdate
except:
    import historicaldate.historicaldate.hdate as hdate

def cycle1(ntries, lo=-365*2500, hi=365*2500):
    "Cycle ordinal -> ymd -> string -> ordinal for ntries random ordinals"
    months = ["Jan", "Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for _ in range(ntries):
        ordinal = random.randint(lo, hi)
        ymd = hdate.to_ymd(ordinal)
        s = f"{ymd.day} {months[ymd.month - 1]} {abs(ymd.year)}"
        if ymd.year < 0:
            s = s + " BCE"
        hd = hdate.HDate(s)
        ord2 = hdate.to_ordinal(hd.pdates["ordinal_mid"])
        assert ordinal == ord2, f"cycle1 failed on input ordinal {ordinal}: ymd={ymd}, s='{s}', ord2={ord2}"

def test1():
    cycle1(1000)