import sys
import os
sys.path.append(os.getcwd())

from historydate import hdate

def compare(s,re_check=None, dcheck=None):
    hd = hdate.HDate(s)
    if re_check is not None:
        found = {k:v for k, v in hd.re_parsed.items() if v != re_check.get(k, None)}
        expected = {k:re_check.get(k,None) for k in found}
        assert found == {}, f"re_check mismatches for '{s}': Found {found} Expected {expected}"

    if dcheck is not None:
        found = {k:v for k, v in hd.d_parsed.items() if v != dcheck.get(k, None)}
        expected = {k:dcheck.get(k,None) for k in found}
        assert found == {}, f"check mismatches for '{s}': Found {found} Expected {expected}"

def test1():
    compare("25 Dec 1066", {'preday':'25','premon':'Dec','year':'1066'}, 
                        {'circa':False,'day':25,'mon':12,'year':1066})
    compare("25th Dec 1066", {'preday':'25','premon':'Dec','year':'1066'}, 
                        {'circa':False,'day':25,'mon':12,'year':1066})
    compare("166",{'year': '166'})
    compare("1066",{'year': '1066'})
    compare("june 1066",{'premon': 'june', 'year': '1066'})
    compare("24 june 1066",{'preday': '24', 'premon': 'june', 'year': '1066'})
    compare("24 Jun 1066",{'preday': '24', 'premon': 'Jun', 'year': '1066'})
    compare("circa 1066-6-24",{'circa': 'circa', 'year': '1066', 'postmon': '6', 'postday': '24'})
    compare("1066 bce",{'year': '1066', 'calendar': 'bce'})
    compare("1483 earliest 1428 latest 1486 ce", 
            {'year': '1483', 'earlyyear': '1428', 'lateyear': '1486', 'latecalendar':'ce'})
    compare("1483 after 1428 before 1486", {'year': '1483', 'earlyyear': '1428', 'lateyear': '1486'})
    compare("after 1428 before 1486", {'earlyyear': '1428', 'lateyear': '1486'})
    compare("circa2y 25 Dec 1066",
            {'circa': 'circa', 'clen': '2', 'clentype': 'y', 
             'preday': '25', 'premon': 'Dec', 'year': '1066'})
