"""
Utilities for figure manipulation in Plotly
"""
import datetime
import plotly.graph_objects as go
from plotly import colors as pc

try:
    import historicaldate.hdate as hdate
except:
    import historicaldate.historicaldate.hdate as hdate

# ----------------------------------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------------
def calc_age(ymd_birth, ymd_ref):
    age = ymd_ref.year - ymd_birth.year
    if ymd_birth.year < 0 and ymd_ref.year > 0:
        age = age - 1   # there is no year 0
    if (ymd_ref.month < ymd_birth.month) or (ymd_ref.month < ymd_birth.month and ymd_ref.day < ymd_birth.day):
        age = age - 1 
    if age < 0:
        raise ValueError("Age calculated as less than 0")
    return age
# ------------------------------------------------------------------------------------
def calc_agetext(pdates_birth, pdates_ref):
    "Calculate age text, including ? to indicate uncertainty"
    ymd_birth_early = hdate.to_ymd(pdates_birth['ordinal_early'])
    ymd_birth_mid = hdate.to_ymd(pdates_birth['ordinal_mid'])
    ymd_birth_late = hdate.to_ymd(pdates_birth['ordinal_late'])
    ymd_ref_early = hdate.to_ymd(pdates_ref['ordinal_early'])
    ymd_ref_mid = hdate.to_ymd(pdates_ref['ordinal_mid'])
    ymd_ref_late = hdate.to_ymd(pdates_ref['ordinal_late'])

    years_largest = calc_age(ymd_birth_early, ymd_ref_late)
    years_smallest = calc_age(ymd_birth_late, ymd_ref_early)
    uncertain = '?' if years_largest > years_smallest else ""

    years = calc_age(ymd_birth_mid, ymd_ref_mid)
    return f"{years}{uncertain}"
# -----------------------------------------------------------------------------------
def calc_yeartext(pdates, hover_datetype='day'):
    if hover_datetype not in {'year','month','day'}:
        raise ValueError(f"hover_datetype must be year, month or day. Found:{hover_datetype}")
    
    ymd_early = hdate.to_ymd(pdates['ordinal_early'])
    ymd_mid = hdate.to_ymd(pdates['ordinal_mid'])
    ymd_late = hdate.to_ymd(pdates['ordinal_late'])

    ytext = str(ymd_mid.year) if ymd_mid.year > 0 else str(-ymd_mid.year) + "BCE"
    if (ymd_early.year != ymd_late.year):
        ytext = ytext + "?"             # Show uncertain year
    if (ymd_early.month == ymd_late.month) and (ymd_early.year == ymd_late.year) and hover_datetype != 'year':
        months = ["Jan", "Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        ytext = f"{months[ymd_mid.month - 1]} {ytext}"
    if (ymd_early == ymd_late) and hover_datetype == 'day':
        ytext = f"{ymd_mid.day} {ytext}"      # Show exact date
    return ytext

# ------------------------------------------------------------------------------------------------    
# -- Now for functions that create the figure
# ------------------------------------------------------------------------------------------------    
def add_trace_marker(fig, pdate=None, label="", y=0.0, 
                   color=None, size=8, symbol='diamond', showlegend=False,
                   hovertext=None, hyperlink=None, xmode="date"):
    "pdate must be an ordinal"
    pltdate = hdate.to_python_date(pdate) if xmode == "date" else hdate.to_years(pdate)
    fig.add_trace(go.Scatter(x = [pltdate], y=[y], name=label, legendgroup=label,
                        mode="markers", marker={'color':color, 'size':size,'symbol':symbol}, 
                        hoverinfo='text',
                        hovertext=hovertext if hovertext else label,
                        hoverlabel={'namelength':-1}, showlegend=showlegend))
# ------------------------------------------------------------------------------------------------
def add_trace_label(fig, pdate=None, label="", y=0.0, hyperlink=None, xmode="date"):
    "pdate must be an ordinal"
    hlinkedtext = f'<a href="{hyperlink}">{label}</a>' if hyperlink else label
    pltdate = hdate.to_python_date(pdate) if xmode == "date" else hdate.to_years(pdate)
    fig.add_trace(go.Scatter(x = [pltdate], y=[y+0.04], 
                                name=label, legendgroup=label,
                                mode="text", text=hlinkedtext, 
                                textposition='bottom center',
                                hoverinfo='skip', hoverlabel={'namelength':-1}, showlegend=False))
# ------------------------------------------------------------------------------------------------

