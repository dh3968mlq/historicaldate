import sys
import datetime

sys.path.append(".")

import historicaldate.hdate as hdate

from utils_for_tests import compare
from utils_for_tests import expect_valueerror

# -- Some BC date checks
def testbc():
    compare("487 bc", 
            dcheck={'circa': False, 'ongoing': False, 'midyear': 487, 'midcalendar': 'bce'},
            pdcheck={'ordinal_early': -177876, 'ordinal_late': -177512, 'ordinal_mid': -177711,
                    'slearly': 'y', 'sllate': 'y', 'slmid': 'y'},
            check_days=True)
    compare("12 July 100 BC",
            pdcheck={'ordinal_early': -36332, 'ordinal_late': -36332, 'ordinal_mid': -36332,
                    'slearly': 'd', 'sllate': 'd', 'slmid': 'd'},
            check_days=True)

def test_sandbox():
    'Put a test here if we want to run it as a one-off'
    compare("487 bc", 
            dcheck={'circa': False, 'ongoing': False, 'midyear': 487, 'midcalendar': 'bce'},
            pdcheck={'ordinal_early': -177876, 'ordinal_late': -177512, 'ordinal_mid': -177711,
                    'slearly': 'y', 'sllate': 'y', 'slmid': 'y'},
            check_days=True)
