"""
Utilities for figure manipulation in Plotly
"""
import datetime
from plotly import colors as pc

class LineOrganiser():
    '''
    Class to find a line to place a trace on
    '''
    def __init__(self, daysperlabelchar=500, daysminspacing = 200):
        self.linerecord = []
        self.daysperlabelchar = daysperlabelchar
        self.daysminspacing = daysminspacing
        self.previoustraceindex = 0
        self.startline = 0

    def reset_startline(self):
        self.startline = len(self.linerecord)

    def add_trace(self, earliest, latest, labeldate, text):
        textdelta = int(len(text) * self.daysperlabelchar/2.0)
        spacingdelta = int(self.daysminspacing/2.0)
        t_earliest = min(earliest, labeldate - textdelta) - spacingdelta
        t_latest = max(latest, labeldate + textdelta) + spacingdelta
        lpd = {"earliest":t_earliest, "latest":t_latest}

        for i in range(self.startline, nlines := len(self.linerecord)):
            line = self.linerecord[(iline := (self.previoustraceindex + i + 1) % nlines)]
            if self.is_available(line, lpd):
                self.linerecord[iline] += [lpd]
                self.previoustraceindex = iline
                return iline

        # Not found
        self.linerecord += [[lpd]]
        #print(self.linerecord)
        self.previoustraceindex = len(self.linerecord) - 1
        return self.previoustraceindex

    def is_available(self, line, lpd):
        return all([self.is_distinct(linepart, lpd) for linepart in line])
    
    def is_distinct(self, lpd1, lpd2):
        #print("isd",lpd1,lpd2)
        return (lpd1["earliest"] > lpd2["latest"]) or (lpd1["latest"] < lpd2["earliest"])

# ---------------------------------------------------------------------------------
class ColorGen():
    def __init__(self):
        self.index = -1
        self.colors = pc.DEFAULT_PLOTLY_COLORS
        self.len = len(self.colors)
    def get(self):
        self.index += 1
        return self.colors[self.index % self.len]