import datetime

import sys
sys.path.insert(0,"./historicaldate") # in case this is run when a submodule

from utils_for_tests import compare
from utils_for_tests import expect_valueerror

def test1():
    compare("25 Dec 1066", {'midpreday':'25','midpremon':'Dec','midyear':'1066'}, 
                        {'circa':False,'ongoing':False,'midday':25,'midmon':12,'midyear':1066})
    compare("25th Dec 1066", {'midpreday':'25','midpremon':'Dec','midyear':'1066'}, 
                        {'circa':False,'ongoing':False,'midday':25,'midmon':12,'midyear':1066})
    compare("166",{'midyear': '166'})
    compare("1066",{'midyear': '1066'})
    compare(1066,{'midyear': '1066'})
    compare("june 1066",{'midpremon': 'june', 'midyear': '1066'})
    compare("24 june 1066",{'midpreday': '24', 'midpremon': 'june', 'midyear': '1066'})
    compare("24 Jun 1066",{'midpreday': '24', 'midpremon': 'Jun', 'midyear': '1066'})
    compare("circa 1066-6-24",{'circa': 'circa', 'midyear': '1066', 
                               'midpostmon': '6', 'midpostday': '24'})
    compare("c. 1066-6-24",{'circa': 'c.', 'midyear': '1066', 
                               'midpostmon': '6', 'midpostday': '24'})
    compare("1066 bce",{'midyear': '1066', 'midcalendar': 'bce'})
    compare("1483 earliest 1428 latest 1486 ce", 
            {'midyear': '1483', 'earlyyear': '1428', 
             'lateyear': '1486', 'latecalendar':'ce'})
    compare("1483 after 1428 before 1486", 
            {'midyear': '1483', 'earlyyear': '1428', 'lateyear': '1486'})
    compare("after 1428 before 1486", {'earlyyear': '1428', 'lateyear': '1486'})
    compare("circa2y 25 Dec 1066",
            {'circa': 'circa', 'clen': '2', 'clentype': 'y', 
             'midpreday': '25', 'midpremon': 'Dec', 'midyear': '1066'},
             {'ongoing': False, 'circa':True, 'clen': '2', 'clentype': 'y', 
              'midday': 25, 'midmon': 12, 'midyear': 1066})
    compare("ongoing",{"ongoing":"ongoing"})

# -- Some pdate checks
def test2():
    compare("25 Dec 1066", 
            pdcheck={'mid': datetime.date(1066, 12, 25), 'slmid': 'd', 
                     'late': datetime.date(1066, 12, 25), 'sllate': 'd', 
                     'early': datetime.date(1066, 12, 25), 'slearly': 'd'})
    compare("1483 after 1428 before 1486", 
            pdcheck={'mid': datetime.date(1483, 6, 15), 'slmid': 'y', 
                     'late': datetime.date(1486, 12, 31), 'sllate': 'y', 
                     'early': datetime.date(1428, 1, 1), 'slearly': 'y'})
    compare("after 1428 before 1486", 
            pdcheck={'mid': datetime.date(1457, 7, 1), 'slmid': 'c', 
                     'late': datetime.date(1486, 12, 31), 'sllate': 'y', 
                     'early': datetime.date(1428, 1, 1), 'slearly': 'y'})
    compare("circa2y 25 Dec 1066", # not exactly two years
            pdcheck={'mid': datetime.date(1066, 12, 25), 'slmid': 'c', 
                     'late': datetime.date(1068, 12, 24), 'sllate': 'c', 
                     'early': datetime.date(1064, 12, 25), 'slearly': 'c'})
    compare("circa 1066-6-24", 
            pdcheck={'mid': datetime.date(1066, 6, 24), 'slmid': 'c', 
                     'late': datetime.date(1071, 6, 24), 'sllate': 'c', 
                     'early': datetime.date(1061, 6, 24), 'slearly': 'c'})
    compare("c. 1066-6-24", 
            pdcheck={'mid': datetime.date(1066, 6, 24), 'slmid': 'c', 
                     'late': datetime.date(1071, 6, 24), 'sllate': 'c', 
                     'early': datetime.date(1061, 6, 24), 'slearly': 'c'})
    compare("c. 1578 ",                          # Also checking trailing space
            pdcheck={'mid': datetime.date(1578, 6, 15), 'slmid': 'c',
                     'late': datetime.date(1583, 6, 15), 'sllate': 'c', 
                     'early': datetime.date(1573, 6, 15), 'slearly': 'c'})
    compare("ongoing",
            pdcheck={'mid':datetime.date.today(), 'slmid': 'o', 'slearly': 'o', 'sllate': 'o', 
                     'late': datetime.date.today() + datetime.timedelta(days=int(5 * 365.25)), 
                     'early': datetime.date.today()})

