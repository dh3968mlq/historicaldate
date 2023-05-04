'''
Class to find a line to place a trace on
'''
import datetime

class LineOrganiser():
    def __init__(self, daysperlabelchar=600):
        self.linerecord = []
        self.daysperlabelchar = daysperlabelchar

    def add_trace(self, earliest, latest, labeldate, text):
        textdelta = datetime.timedelta(days=int(len(text) * self.daysperlabelchar/2.0))
        t_earliest = min(earliest, labeldate - textdelta)
        t_latest = max(latest, labeldate + textdelta)
        lpd = {"earliest":t_earliest, "latest":t_latest}
        for iline, line in enumerate(self.linerecord):
            if self.is_available(line, lpd):
                self.linerecord[iline] += [lpd]
                return iline

        # Not found
        self.linerecord += [[lpd]]
        #print(self.linerecord)
        return len(self.linerecord) - 1

    def is_available(self, line, lpd):
        return all([self.is_distinct(linepart, lpd) for linepart in line])
    
    def is_distinct(self, lpd1, lpd2):
        #print("isd",lpd1,lpd2)
        return (lpd1["earliest"] > lpd2["latest"]) or (lpd1["latest"] < lpd2["earliest"])