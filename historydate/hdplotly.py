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

def add_trace_part(fig, pdate_start=None, pdate_end=None, label="", y=0.0, color=None, 
                   width=4, dash=None, showlegend=False, showlabel=False,
                   hovertext=None):
    if (pdate_start < pdate_end) or showlegend:
        xs = [pdate_start] + \
             [datetime.date(year, 1, 1) for year in range(pdate_start.year + 1, pdate_end.year + 1)] + \
             [pdate_end]
        ys = [y for _ in xs]
        fig.add_trace(go.Scatter(x = xs, y=ys, name=label, legendgroup=label,
                            mode="lines", line={'color':color,'width':width,'dash':dash}, 
                            hoverinfo='text',
                            hovertext=hovertext if hovertext else label,
                            hoverlabel={'namelength':-1}, showlegend=showlegend))
        # Show the label if required
        if showlabel:
            fig.add_trace(go.Scatter(x = [pdate_start + (pdate_end - pdate_start)/2.0], y=[y-0.04], 
                                     name=label, legendgroup=label,
                            mode="text", text=label, textposition='bottom center',
                            hoverinfo='skip', hoverlabel={'namelength':-1}, showlegend=False))

def calc_pdates(ahdate):
    hd = hdate.HDate(ahdate)
    return hd.pdates

def calc_yeartext(pdates):
    return str(pdates['core'].year) + \
                ("" if pdates['early'].year == pdates['late'].year else "?")

def add_timeline_trace(fig, row, y=0.0, showbirthanddeath=False, showlegend=True, color=None):
    '''
    Add a timeline trace for a given row
    '''
    pdates_start = calc_pdates(row["hdate"])
    pdates_end = calc_pdates(row["hdate_end"])
    
    text = row["label"]

    # -- Main part
    hovertext = f"{text} ({calc_yeartext(pdates_start)}-{calc_yeartext(pdates_end)})"
    add_trace_part(fig, pdate_start=pdates_start['late'], pdate_end=pdates_end['early'], 
                   label=text, y=y, color=color, showlegend=showlegend, showlabel=True,
                   hovertext=hovertext)
    add_trace_part(fig, pdate_start=pdates_start['early'], pdate_end=pdates_start['late'], 
                   label=text, y=y, color=color, width=1, hovertext=hovertext)
    add_trace_part(fig, pdate_start=pdates_end['early'], pdate_end=pdates_end['late'], 
                   label=text, y=y, color=color, width=1, hovertext=hovertext)
    
    if showbirthanddeath:
        pdates_birth = calc_pdates(row["hdate_birth"])
        hovertext = f"{text} (b. {calc_yeartext(pdates_birth)})"
        add_trace_part(fig, pdate_start=pdates_birth['late'], pdate_end=pdates_start['early'], 
               label=text, y=y, color=color, dash='dot', hovertext=hovertext)
        add_trace_part(fig, pdate_start=pdates_birth['early'], pdate_end=pdates_birth['late'], 
                   label=text, y=y, color=color, width=1, dash='dot', hovertext=hovertext)

        pdates_death = calc_pdates(row["hdate_death"])
        hovertext = f"{text} (d. {calc_yeartext(pdates_death)})"
        add_trace_part(fig, pdate_start=pdates_end['late'], pdate_end=pdates_death['early'], 
                   label=text, y=y, color=color, dash='dot', hovertext=hovertext)
        add_trace_part(fig, pdate_start=pdates_death['early'], pdate_end=pdates_death['late'], 
                   label=text, y=y, color=color, width=1, dash='dot', hovertext=hovertext)
