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
        "Reset the start line to the maximum already used by this LineOrganiser object"
        self.startline = len(self.linerecord)

    def add_trace(self, earliest, latest, labeldate, text):
        """
        Find a line to display a trace on

        * earliest, latest: the start and end dates of the trace (HDate ordinals)
        * labeldate: the position the label will be displayed at (HDate ordinal)
        * text: the label text
        
        add_trace returns a line number that the trace can be displayed on
        """
        textdelta = int(len(text) * self.daysperlabelchar/2.0)
        spacingdelta = int(self.daysminspacing/2.0)
        t_earliest = min(earliest, labeldate - textdelta) - spacingdelta
        t_latest = max(latest, labeldate + textdelta) + spacingdelta
        lpd = {"earliest":t_earliest, "latest":t_latest}

        for i in range(self.startline, nlines := len(self.linerecord)):
            line = self.linerecord[(iline := (self.previoustraceindex + i + 1) % nlines)]
            if self._is_available(line, lpd):
                self.linerecord[iline] += [lpd]
                self.previoustraceindex = iline
                return iline

        # Not found
        self.linerecord += [[lpd]]
        #print(self.linerecord)
        self.previoustraceindex = len(self.linerecord) - 1
        return self.previoustraceindex

    def _is_available(self, line, lpd):
        return all([self._is_distinct(linepart, lpd) for linepart in line])
    
    def _is_distinct(self, lpd1, lpd2):
        #print("isd",lpd1,lpd2)
        return (lpd1["earliest"] > lpd2["latest"]) or (lpd1["latest"] < lpd2["earliest"])
