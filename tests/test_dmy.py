import sys
import datetime

sys.path.append(".")

try:
    import historicaldate.hdate as hdate
except:
    import historicaldate.historicaldate.hdate as hdate

from utils_for_tests import compare
from utils_for_tests import expect_valueerror

# -- Some prefixdateorder checks
def test_mdy():
    expect_valueerror("25/12/1066")
    expect_valueerror("12/25/1066", prefixdateorder="dmy")
    compare("25/12/1066", prefixdateorder="dmy",
            pdcheck={'mid': datetime.date(1066, 12, 25), 'slmid': 'd', 
                     'late': datetime.date(1066, 12, 25), 'sllate': 'd', 
                     'early': datetime.date(1066, 12, 25), 'slearly': 'd'})
    compare("1066-12-25", prefixdateorder="dmy",
            pdcheck={'mid': datetime.date(1066, 12, 25), 'slmid': 'd', 
                     'late': datetime.date(1066, 12, 25), 'sllate': 'd', 
                     'early': datetime.date(1066, 12, 25), 'slearly': 'd'})
