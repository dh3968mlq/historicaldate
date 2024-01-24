import sys
sys.path.insert(0,".") # For Github
sys.path.insert(0,"./historicaldate") # in case this is run when a submodule

import datetime
from utils_for_tests import compare
from utils_for_tests import expect_valueerror

# -- Some BC date checks
def testbc():
    compare("487 bc", 
            dcheck={'circa': False, 'ongoing': False, 'midyear': 487, 'midcalendar': 'bce', 'earlycalendar': 'bce'},
            pdcheck={'ordinal_early': -177876, 'ordinal_late': -177512, 'ordinal_mid': -177711,
                    'slearly': 'y', 'sllate': 'y', 'slmid': 'y'},
            check_days=True)
    compare("12 July 100 BC",
            pdcheck={'ordinal_early': -36332, 'ordinal_late': -36332, 'ordinal_mid': -36332,
                    'slearly': 'd', 'sllate': 'd', 'slmid': 'd'},
            check_days=True)
    compare("12 July 100BCe",
            pdcheck={'ordinal_early': -36332, 'ordinal_late': -36332, 'ordinal_mid': -36332,
                    'slearly': 'd', 'sllate': 'd', 'slmid': 'd'},
            check_days=True)
    compare("c. 287BC",
            pdcheck={'ordinal_early': -106487, 'ordinal_late': -102835, 'ordinal_mid': -104661,
                    'slearly': 'c', 'sllate': 'c', 'slmid': 'c'},
            check_days=True)
    compare("c. 287BC",
            pdcheck={'ordinal_early': -106487, 'ordinal_late': -102835, 'ordinal_mid': -104661,
                    'slearly': 'c', 'sllate': 'c', 'slmid': 'c'},
            check_days=True, dateformat="mdy")
    compare("Between 500BC and 400BC",
            pdcheck={'ordinal_mid': -164180, 'slmid': 'c', 'ordinal_late': -145735, 'sllate': 'y', 'ordinal_early': -182624, 'slearly': 'y'},
            check_days=True)
    compare("Between 500 and 400BC",
            pdcheck={'ordinal_mid': -164180, 'slmid': 'c', 'ordinal_late': -145735, 'sllate': 'y', 'ordinal_early': -182624, 'slearly': 'y'},
            check_days=True)
    compare("Before 400BC",
            pdcheck={'ordinal_mid': -147561, 'slmid': 'c', 'ordinal_late': -145735, 'sllate': 'y', 'ordinal_early': -149387, 'slearly': 'c'},
            check_days=True)
    compare("Between 27BC and 14AD",
            pdcheck={'ordinal_mid': -2374, 
                     'late': datetime.date(14, 12, 31), 'ordinal_late': 5113, 
                     'ordinal_early': -9861, 
                     'slearly': 'y', 'slmid': 'c', 'sllate': 'y'},
            check_days=True)

def test_sandbox():
    'Put a test here if we want to run it as a one-off'
    compare("487 bc", 
            dcheck={'circa': False, 'ongoing': False, 'midyear': 487, 'midcalendar': 'bce', 'earlycalendar': 'bce'},
            pdcheck={'ordinal_early': -177876, 'ordinal_late': -177512, 'ordinal_mid': -177711,
                    'slearly': 'y', 'sllate': 'y', 'slmid': 'y'},
            check_days=True)
