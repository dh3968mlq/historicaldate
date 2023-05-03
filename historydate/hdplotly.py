"""
Plotly timelines for historydate package
"""
import sys
sys.path.append("..")

import datetime
import plotly.graph_objects as go
from plotly import colors as pc
from historydate import hdate

class plTimeLine():
    def __init__(self, mindate=None, maxdate=None):
        self.figure = go.Figure()
        self.maxdate = datetime.date.today() + datetime.timedelta(days=int(10*365.25)) \
                            if maxdate is None else maxdate
        self.mindate = self.maxdate - datetime.timedelta(days=int(200*365.25)) \
                            if mindate is None else mindate

        self.fig_config = {'scrollZoom': True, 'displayModeBar':None}

        self.figure.update_layout(dragmode="pan", showlegend=False)
        self.figure.update_xaxes(
                            tickangle = 90,
                            title_text = "Date",
                            title_font = {"size": 20},
                            title_standoff = 25,
                            range=[self.mindate, self.maxdate])
        self.max_y_used = 0.0
# -------------
    def add_event_set(self, df, nrows=8, rowspacing=0.3,
                    title="", showbirthanddeath=False):
        """
        df must have column 'hdate'
        Optional columns:
            label: String label or identifier
            hdate_end: end of persistent event. hdate is interpreted as the start date.
            If hdate_end is absent, events are treated as single-date events, not persistent events.
            hdate_birth, hdate_death: Birth and death dates
        """
        colgen = ColorGen()
        if title:
            self.figure.add_annotation(text=f"<b>{title}</b>", 
                    x=0.02, xref='paper', y=self.max_y_used, 
                    showarrow=False, font={'size':16})
        for irow, row in df.sort_values('hdate').iterrows():  # >> Get the sortation right!
            color = colgen.get()
            add_timeline_trace(self.figure, row, 
                            y=self.max_y_used + (irow % nrows + 1) * rowspacing, 
                            showbirthanddeath=showbirthanddeath, color=color)
        self.max_y_used += (nrows + 2) * rowspacing    
# -------------
    def show(self,fix_y_range=False):
        self.figure.update_yaxes(range=[self.max_y_used+0.25,-0.25], 
                                 visible=False, fixedrange=fix_y_range)
        self.figure.show(config=self.fig_config)
# -------------
    def write_html(self, filename):
        self.figure.update_yaxes(range=[self.max_y_used+0.25,-0.25], 
                                 visible=False, fixedrange=True)
        self.figure.write_html(filename,include_plotlyjs='cdn', config=self.fig_config)
# ------------------------------------------------------------------------------------------------
class ColorGen():
    def __init__(self):
        self.index = -1
        self.colors = pc.DEFAULT_PLOTLY_COLORS
        self.len = len(self.colors)
    def get(self):
        self.index += 1
        return self.colors[self.index % self.len]
# ------------------------------------------------------------------------------------------------
def add_trace_marker(fig, pdate=None, label="", y=0.0, 
                   color=None, size=10, symbol='diamond', showlegend=False, showlabel=False,
                   hovertext=None, hyperlink=None):
    # Show the label if required
    if showlabel:
        hlinkedtext = f'<a href="{hyperlink}">{label}</a>' if hyperlink else label
        fig.add_trace(go.Scatter(x = [pdate], 
                                 y=[y+0.04], 
                                    name=label, legendgroup=label,
                        mode="text", text=hlinkedtext, 
                        textposition='bottom center',
                        hoverinfo='skip', hoverlabel={'namelength':-1}, showlegend=False))
    # Draw marker
    fig.add_trace(go.Scatter(x = [pdate], y=[y], name=label, legendgroup=label,
                        mode="markers", marker={'color':color, 'size':size,'symbol':symbol}, 
                        hoverinfo='text',
                        hovertext=hovertext if hovertext else label,
                        hoverlabel={'namelength':-1}, showlegend=showlegend))

# ------------------------------------------------------------------------------------------------
def add_trace_part(fig, pdate_start=None, pdate_end=None, label="", y=0.0, 
                   ongoing=False, color=None, 
                   width=4, dash=None, showlegend=False, showlabel=False,
                   hovertext=None, tdelta=5*365.25,
                   hyperlink=None):
    if ongoing:
        pdate_end_local = pdate_start + datetime.timedelta(days=tdelta)
        dash_local = 'dot'
    else:
        pdate_end_local = pdate_end 
        dash_local = dash 

    if (pdate_start < pdate_end_local): 
        # Show the label if required
        if showlabel:
            hlinkedtext = f'<a href="{hyperlink}">{label}</a>' if hyperlink else label
            fig.add_trace(go.Scatter(x = [pdate_start + (pdate_end_local - pdate_start)/2.0], 
                                    y=[y+0.04], # -0.04], 
                                        name=label, legendgroup=label,
                            mode="text", text=hlinkedtext, 
                            textposition='bottom center',
                            hoverinfo='name', hoverlabel={'namelength':-1}, showlegend=False))
        # Main part of the trace
        xs = [pdate_start] + \
             [datetime.date(year, 1, 1) for year in 
                    range(pdate_start.year + 1, pdate_end_local.year + 1)] + [pdate_end_local]
        ys = [y for _ in xs]
        fig.add_trace(go.Scatter(x = xs, y=ys, name=label, legendgroup=label,
                            mode="lines", line={'color':color,'width':width,'dash':dash_local}, 
                            hoverinfo='text',
                            hovertext=hovertext if hovertext else label,
                            hoverlabel={'namelength':-1}, showlegend=False))
        
        if ongoing:     # -- Add 'ongoing' arrow
            fig.add_trace(go.Scatter(x = [pdate_end_local + datetime.timedelta(days=300)], y=[y], 
                            name=label, legendgroup=label,
                            mode="markers", marker={'color':color,'symbol':'arrow-right','size':12}, 
                            hoverinfo='skip', showlegend=False))
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
    try:
        pdates_end = calc_pdates(row["hdate_end"])
    except TypeError:
        pdates_end = None

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
                   ongoing=ongoing, 
                   label=text, y=y, color=color, showlabel=True,
                   hovertext=hovertext, hyperlink=row['wikipedia_url'])
    add_trace_marker(fig, pdate=pdates_start['core'], y=y, color=color,
                     showlegend=showlegend, 
                    hovertext=hovertext, hyperlink=row['wikipedia_url'])
    if not ongoing:
        add_trace_part(fig, pdate_start=pdates_end['early'], pdate_end=pdates_end['late'], 
                       label=text, y=y, color=color, width=1, hovertext=hovertext)
        add_trace_marker(fig, pdate=pdates_end['core'], y=y, color=color,
                    hovertext=hovertext, hyperlink=row['wikipedia_url'])
    
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
# ------------------------------------------------------------------------------------------------
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
    add_trace_marker(fig, pdate=pdates['core'], 
                   label=text, y=y, color=color, showlegend=showlegend, showlabel=True,
                   hovertext=hovertext, hyperlink=row['wikipedia_url'])
    