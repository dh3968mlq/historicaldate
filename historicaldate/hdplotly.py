"""
Plotly timelines for historicaldate package
"""
import sys
sys.path.append("..")

import datetime
import plotly.graph_objects as go
from plotly import colors as pc
from historicaldate import hdate
from historicaldate import lineorganiser

class plTimeLine():
    def __init__(self, mindate=None, maxdate=None):
        self.figure = go.Figure()
        self.figure.update_layout(xaxis_title=None, title=None, margin={'l':0,'r':0,'t':0,'b':0})
        self.maxdate = datetime.date.today() + datetime.timedelta(days=int(10*365.25)) \
                            if maxdate is None else maxdate
        self.mindate = self.maxdate - datetime.timedelta(days=int(200*365.25)) \
                            if mindate is None else mindate

        self.fig_config = {'scrollZoom': True} #, 'displayModeBar':None}
        self.figure.update_layout(dragmode="pan", showlegend=False)
        self.figure.update_xaxes(
                            #tickangle = 90,
                            #title_text = "Date",
                            #title_font = {"size": 14},
                            #title_standoff = 10,
                            range=[self.mindate, self.maxdate])
        self.max_y_used = 0.0
# -------------
    def add_event_set(self, df, 
                    title="", showbirthanddeath=False, showlabel=True,
                      rowspacing=0.3):
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
                    showarrow=False, font={'size':14})
        df["_hdplsortorder"] = df["hdate"].apply(hdate.calc_core_date)
        lo = lineorganiser.LineOrganiser()
        for _, row in df.sort_values("_hdplsortorder").iterrows():  
            color = colgen.get()
            self.add_timeline_trace(row, 
                            showbirthanddeath=showbirthanddeath, showlabel=showlabel,
                            color=color, lo=lo)
        self.max_y_used += (len(lo.linerecord) + 2) * rowspacing    
# -------------
    def add_timeline_trace(self, row, showbirthanddeath=False, 
                        showlegend=False, showlabel=True,
                        color=None, lo=None):
        try:
            pdates_end = calc_pdates(row["hdate_end"])
        except TypeError:
            pdates_end = None

        if pdates_end:
            self.add_timeline_trace_persistent(row,
                    showbirthanddeath=showbirthanddeath, showlabel=showlabel,
                    showlegend=showlegend, color=color, lo=lo)
        else:
            self.add_timeline_trace_event(row,  
                    showlegend=showlegend, showlabel=showlabel,
                    color=color, lo=lo)
# -------------
    def add_timeline_trace_persistent(self, row, showbirthanddeath=False, 
                                    showlegend=True, showlabel=True,
                                    color=None, lo=None, rowspacing=0.3):
        '''
        Add a persistent timeline trace for a given row
        'persistent' is defined by hdate_end is not None
        '''        
        fig = self.figure
        cols = list(row.index)
        text = row["label"]
        htext = row["description"] if "description" in cols else text
        pdates_start = calc_pdates(row["hdate"])

        pdates_end = calc_pdates(row["hdate_end"]) if "hdate_end" in cols else None
        ongoing = pdates_end['slcore'] == 'o' if pdates_end else False

        if ongoing:
            hovertext = f"{htext} ({calc_yeartext(pdates_start)}...)"
        else:
            hovertext = f"{htext} ({calc_yeartext(pdates_start)}-{calc_yeartext(pdates_end)})"

        earliest = pdates_start['early']
        latest = pdates_end['late']

        if showbirthanddeath:
            if pdates_birth := calc_pdates(row["hdate_birth"]):
                earliest = min(earliest, pdates_birth['early'])
            if pdates_death := calc_pdates(row["hdate_death"]):
                latest = max(latest, pdates_death['late'])

        labeldate = pdates_start['core'] + (pdates_end['core'] - pdates_start['core'])/2.0
        iline = lo.add_trace(earliest, latest, labeldate, text if showlabel else "")
        y = self.max_y_used + (iline + 1) * rowspacing
        
        # Main part, from hdate to hdate_end
        add_trace_part(fig, pdate_start=pdates_start['early'], pdate_end=pdates_start['late'], 
                    label=text, y=y, color=color, width=1, hovertext=hovertext)
        add_trace_part(fig, pdate_start=pdates_start['late'], 
                    pdate_end=pdates_end['early'], 
                    label=text, y=y, color=color, showlabel=showlabel,
                    hovertext=hovertext, hyperlink=row['wikipedia_url'])
        add_trace_marker(fig, pdate=pdates_start['core'], y=y, color=color,
                        showlegend=showlegend, 
                        hovertext=hovertext, hyperlink=row['wikipedia_url'])
        add_trace_part(fig, pdate_start=pdates_end['early'], pdate_end=pdates_end['late'], 
                        label=text, y=y, color=color, width=1, hovertext=hovertext)

        if ongoing:   # Right arrow at end of 'ongoing' period
            add_trace_marker(fig, pdate=pdates_end['late'], y=y, color=color,
                        symbol='arrow-right',
                        hovertext=hovertext, hyperlink=row['wikipedia_url'])
        else:        # Normal marker at end of period
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
# -------------
    def add_timeline_trace_event(self, row, 
                                 showlegend=True, showlabel=False,
                                 color=None, lo=None, rowspacing=0.3):
        '''
        Add timeline trace for an event
        Initial implementation: no births and deaths
        '''
        text = row["label"]
        pdates = calc_pdates(row["hdate"])

        hovertext = f"{text} ({calc_yeartext(pdates)})"
        iline = lo.add_trace(pdates["early"], pdates["late"], pdates["core"], text if showlabel else "")
        y = self.max_y_used + (iline + 1) * rowspacing

        add_trace_part(self.figure, pdate_start=pdates['early'], pdate_end=pdates['late'], 
                    label=text, y=y, color=color, width=1, hovertext=hovertext)
        add_trace_marker(self.figure, pdate=pdates['core'], 
                    label=text, y=y, color=color, showlegend=showlegend, showlabel=showlabel,
                    hovertext=hovertext, hyperlink=row['wikipedia_url'])
    
# -------------
    def show(self,fix_y_range=False):
        self.figure.update_yaxes(range=[self.max_y_used+0.25,-0.25], 
                                 visible=False, fixedrange=fix_y_range)
        self.figure.show(config=self.fig_config)
# -------------
    def write_html(self, filename, fix_y_range=False):
        self.figure.update_yaxes(range=[self.max_y_used+0.25,-0.25], 
                                 visible=False, fixedrange=fix_y_range)
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
                   color=None, 
                   width=4, dash=None, showlabel=False,
                   hovertext=None, 
                   hyperlink=None):

    if (pdate_start <= pdate_end): 
        # Show the label if required
        if showlabel:
            hlinkedtext = f'<a href="{hyperlink}">{label}</a>' if hyperlink else label
            fig.add_trace(go.Scatter(x = [pdate_start + (pdate_end - pdate_start)/2.0], 
                                    y=[y+0.04], 
                                        name=label, legendgroup=label,
                            mode="text", text=hlinkedtext, 
                            textposition='bottom center',
                            hoverinfo='name', hoverlabel={'namelength':-1}, showlegend=False))
        # Main part of the trace
        xs = [pdate_start] + \
             [datetime.date(year, 1, 1) for year in 
                    range(pdate_start.year + 1, pdate_end.year + 1)] + [pdate_end]
        ys = [y for _ in xs]
        fig.add_trace(go.Scatter(x = xs, y=ys, name=label, legendgroup=label,
                            mode="lines", line={'color':color,'width':width,'dash':dash}, 
                            hoverinfo='text',
                            hovertext=hovertext if hovertext else label,
                            hoverlabel={'namelength':-1}, showlegend=False))
# ------------------------------------------------------------------------------------------------
def calc_pdates(ahdate):
    hd = hdate.HDate(ahdate)
    return hd.pdates
# ------------------------------------------------------------------------------------------------
def calc_yeartext(pdates):
    return str(pdates['core'].year) + \
                ("" if pdates['early'].year == pdates['late'].year else "?")
