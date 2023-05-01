"""
Plotly timelines for historydate package
"""
import sys
sys.path.append("..")

import datetime
import plotly.graph_objects as go
from historydate import hdate

class plTimeLine():
    def __init__(self):
        self.figure = go.Figure()

    def add_hdate_traces(df):
        """
        df must have column 'hdate'
        Optional columns:
            label: String label or identifier
            hdate_end: end of persistent event. hdate is interpreted as the start date.
                If hdate_end is absent, events are treated as single-date events, not persistent events.
            hdate_birth, hdate_death: Birth and death dates
        """
        ...

# ------------------------------------------------------------------------------------------------

def add_trace_part(fig, pdate_start=None, pdate_end=None, label="", y=0.0, 
                   ongoing=False, eventful=False, color=None, 
                   width=4, dash=None, showlegend=False, showlabel=False,
                   hovertext=None, tdelta=5*365.25,
                   hyperlink=None):
    if ongoing:
        pdate_end_local = pdate_start + datetime.timedelta(days=tdelta)
        dash_local = 'dot'
    else:
        pdate_end_local = pdate_end 
        dash_local = dash 

    if eventful and ((pdate_end_local is None) or (pdate_start == pdate_end_local)):
        xs = [pdate_start]
        ys = [y]
        fig.add_trace(go.Scatter(x = xs, y=ys, name=label, legendgroup=label,
                            mode="markers", marker={'color':color}, 
                            hoverinfo='text',
                            hovertext=hovertext if hovertext else label,
                            hoverlabel={'namelength':-1}, showlegend=showlegend))
    elif (pdate_start < pdate_end_local): #or showlegend: # showlegend may be irrelevant
        xs = [pdate_start] + \
             [datetime.date(year, 1, 1) for year in 
                    range(pdate_start.year + 1, pdate_end_local.year + 1)] + [pdate_end_local]
        ys = [y for _ in xs]
        fig.add_trace(go.Scatter(x = xs, y=ys, name=label, legendgroup=label,
                            mode="lines", line={'color':color,'width':width,'dash':dash_local}, 
                            hoverinfo='text',
                            hovertext=hovertext if hovertext else label,
                            hoverlabel={'namelength':-1}, showlegend=showlegend))
        
        if ongoing:     # -- Add 'ongoing' arrow
            fig.add_trace(go.Scatter(x = [pdate_end_local + datetime.timedelta(days=300)], y=[y], 
                            name=label, legendgroup=label,
                            mode="markers", marker={'color':color,'symbol':'arrow-right','size':12}, 
                            hoverinfo='skip', showlegend=False))

    # Show the label if required
    if showlabel:
        hlinkedtext = f'<a href="{hyperlink}">{label}</a>' if hyperlink else label
        fig.add_trace(go.Scatter(x = [pdate_start + (pdate_end_local - pdate_start)/2.0], 
                                 y=[y+0.04], # -0.04], 
                                    name=label, legendgroup=label,
                        mode="text", text=hlinkedtext, 
                        textposition='bottom center',
                        hoverinfo='skip', hoverlabel={'namelength':-1}, showlegend=False))

# ------------------------------------------------------------------------------------------------
def calc_pdates(ahdate):
    hd = hdate.HDate(ahdate)
    return hd.pdates
# ------------------------------------------------------------------------------------------------
def calc_yeartext(pdates):
    return str(pdates['core'].year) + \
                ("" if pdates['early'].year == pdates['late'].year else "?")
# ------------------------------------------------------------------------------------------------

def add_timeline_trace(fig, row, y=0.0, showbirthanddeath=False, showlegend=True, color=None):
    pdates_end = calc_pdates(row["hdate_end"])
    if pdates_end:
       add_timeline_trace_persistent(fig, row, y=y, 
                showbirthanddeath=showbirthanddeath, 
                showlegend=showlegend, color=color)
    else:
       add_timeline_trace_event(fig, row, y=y, 
                showlegend=showlegend, color=color)

# ------------------------------------------------------------------------------------------------

def add_timeline_trace_persistent(fig, row, y=0.0, 
                                  showbirthanddeath=False, showlegend=True, color=None):
    '''
    Add a persistent timeline trace for a given row
    'persistent' is defined by hdate_end is not None
    '''
    
    text = row["label"]
    pdates_start = calc_pdates(row["hdate"])
    pdates_end = calc_pdates(row["hdate_end"])
    ongoing = pdates_end["ongoing"]

    if ongoing:
        hovertext = f"{text} ({calc_yeartext(pdates_start)}...)"
    else:
        hovertext = f"{text} ({calc_yeartext(pdates_start)}-{calc_yeartext(pdates_end)})"

    # Main part, from hdate to hdate_end
    add_trace_part(fig, pdate_start=pdates_start['early'], pdate_end=pdates_start['late'], 
                   label=text, y=y, color=color, width=1, hovertext=hovertext)
    add_trace_part(fig, pdate_start=pdates_start['late'], 
                   pdate_end=pdates_end['early'], 
                   ongoing=ongoing, eventful=True,
                   label=text, y=y, color=color, showlegend=showlegend, showlabel=True,
                   hovertext=hovertext, hyperlink=row['wikipedia_url'])
    if not ongoing:
        add_trace_part(fig, pdate_start=pdates_end['early'], pdate_end=pdates_end['late'], 
                       label=text, y=y, color=color, width=1, hovertext=hovertext)
    
    if showbirthanddeath:
        if pdates_birth := calc_pdates(row["hdate_birth"]):
            hovertext = f"{text} (b. {calc_yeartext(pdates_birth)})"
            add_trace_part(fig, pdate_start=pdates_birth['late'], 
                                pdate_end=pdates_start['early'], 
                label=text, y=y, color=color, dash='dot', hovertext=hovertext)
            add_trace_part(fig, pdate_start=pdates_birth['early'], pdate_end=pdates_birth['late'], 
                    label=text, y=y, color=color, width=1, dash='dot', hovertext=hovertext)

        if pdates_death := calc_pdates(row["hdate_death"]):
            hovertext = f"{text} (d. {calc_yeartext(pdates_death)})"
            add_trace_part(fig, pdate_start=pdates_end['late'], pdate_end=pdates_death['early'], 
                   label=text, y=y, color=color, dash='dot', hovertext=hovertext)
            add_trace_part(fig, pdate_start=pdates_death['early'], pdate_end=pdates_death['late'], 
                   label=text, y=y, color=color, width=1, dash='dot', hovertext=hovertext)

def add_timeline_trace_event(fig, row, y=0.0, showlegend=True, color=None):
    '''
    Add timeline trace for an event
    Initial implementation: no births and deaths
    '''
    
    text = row["label"]
    pdates = calc_pdates(row["hdate"])

    hovertext = f"{text} ({calc_yeartext(pdates)})"

    add_trace_part(fig, pdate_start=pdates['early'], pdate_end=pdates['late'], 
                   label=text, y=y, color=color, width=1, hovertext=hovertext)
    add_trace_part(fig, pdate_start=pdates['core'], eventful=True,
                   label=text, y=y, color=color, showlegend=showlegend, showlabel=True,
                   hovertext=hovertext, hyperlink=row['wikipedia_url'])
    