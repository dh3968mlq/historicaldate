import datetime

import sys
sys.path.insert(0,"./historicaldate") # in case this is run when a submodule

from utils_for_tests import compare
from utils_for_tests import expect_valueerror

# -- Some dateformat checks
def test_dmy():
    expect_valueerror("25/12/1066")
    expect_valueerror("12/25/1066", dateformat="dmy")
    compare("25/12/1066", dateformat="dmy",
            pdcheck={'mid': datetime.date(1066, 12, 25), 'slmid': 'd', 
                     'late': datetime.date(1066, 12, 25), 'sllate': 'd', 
                     'early': datetime.date(1066, 12, 25), 'slearly': 'd'})
    compare("1066-12-25", dateformat="dmy",
            pdcheck={'mid': datetime.date(1066, 12, 25), 'slmid': 'd', 
                     'late': datetime.date(1066, 12, 25), 'sllate': 'd', 
                     'early': datetime.date(1066, 12, 25), 'slearly': 'd'})

    compare("25 Dec, 1066",  dateformat="dmy",
            pdcheck={'mid': datetime.date(1066, 12, 25), 'slmid': 'd', 
                     'late': datetime.date(1066, 12, 25), 'sllate': 'd', 
                     'early': datetime.date(1066, 12, 25), 'slearly': 'd'})
    compare("1483 after 1428 before 1486",  dateformat="dmy",
            pdcheck={'mid': datetime.date(1483, 6, 15), 'slmid': 'y', 
                     'late': datetime.date(1486, 12, 31), 'sllate': 'y', 
                     'early': datetime.date(1428, 1, 1), 'slearly': 'y'})
    compare("after 1428 before 1486",  dateformat="dmy",
            pdcheck={'mid': datetime.date(1457, 7, 1), 'slmid': 'c', 
                     'late': datetime.date(1486, 12, 31), 'sllate': 'y', 
                     'early': datetime.date(1428, 1, 1), 'slearly': 'y'})
    compare("circa2y 25/12/1066", dateformat="dmy", # not exactly two years
            pdcheck={'mid': datetime.date(1066, 12, 25), 'slmid': 'c', 
                     'late': datetime.date(1068, 12, 24), 'sllate': 'c', 
                     'early': datetime.date(1064, 12, 25), 'slearly': 'c'})
    compare("circa 1066-6-24", dateformat="dmy", 
            pdcheck={'mid': datetime.date(1066, 6, 24), 'slmid': 'c', 
                     'late': datetime.date(1071, 6, 24), 'sllate': 'c', 
                     'early': datetime.date(1061, 6, 24), 'slearly': 'c'})
    compare("c. 1066-6-24",  dateformat="dmy",
            pdcheck={'mid': datetime.date(1066, 6, 24), 'slmid': 'c', 
                     'late': datetime.date(1071, 6, 24), 'sllate': 'c', 
                     'early': datetime.date(1061, 6, 24), 'slearly': 'c'})
    compare("c. 1578 ", dateformat="dmy",     # Also checking trailing space
            pdcheck={'mid': datetime.date(1578, 6, 15), 'slmid': 'c',
                     'late': datetime.date(1583, 6, 15), 'sllate': 'c', 
                     'early': datetime.date(1573, 6, 15), 'slearly': 'c'})
    compare("ongoing", dateformat="dmy",
            pdcheck={'mid':datetime.date.today(), 'slmid': 'o', 'slearly': 'o', 'sllate': 'o', 
                     'late': datetime.date.today() + datetime.timedelta(days=int(5 * 365.25)), 
                     'early': datetime.date.today()})
