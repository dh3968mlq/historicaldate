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

        self.fig_config = {'scrollZoom': True}
        self.figure.update_layout(dragmode="pan", showlegend=False)
        self.figure.update_xaxes(range=[self.mindate, self.maxdate])
        self.max_y_used = 0.0
# -------------
    def add_event_set(self, df, 
                    title="", showbirthanddeath=True, showlabel=True,
                      rowspacing=0.3):
        """
        dates are in df columns: hdate, hdate_end, hdate_birth, hdate_death
        df must include either hdate or both of hdate_birth, hdate_death

        Other columns:
            label: String label or identifier (required)
            text: Hovertext (optional, defaults to label)
            url: hyperlink (optional)
        """
        colorgen = ColorGen()
        colorcol = "color" if "color" in df.columns \
                    else "colour" if "colour" in df.columns \
                    else ""
        if title:
            self.figure.add_annotation(text=f"<b>{title}</b>", 
                    x=0.02, xref='paper', y=self.max_y_used, 
                    showarrow=False, font={'size':14})
        if "hdate" in df.columns:
            df["_hdplsortorder"] = df["hdate"].apply(hdate.calc_core_date)
            dfs = df.sort_values("_hdplsortorder")
        else:
            dfs = df

        lo = lineorganiser.LineOrganiser()
        for _, row in dfs.iterrows():  
            color = row[colorcol] if colorcol else colorgen.get()
            self.add_timeline_trace(row, 
                            showbirthanddeath=showbirthanddeath, showlabel=showlabel,
                            color=color, lo=lo)
        self.max_y_used += (len(lo.linerecord) + 2) * rowspacing    
# -------------
    def add_timeline_trace(self, row, showbirthanddeath=False, 
                                    showlegend=True, showlabel=True,
                                    color=None, lo=None, rowspacing=0.3):
        '''
        Add a timeline trace for a given row
        '''        
        fig = self.figure
        cols = list(row.index)
        text = row["label"]
        htext = row["description"] if "description" in cols else text
        hlink = row['url'] if 'url' in cols else None

        earliest, latest = None, None

        # Function to get a date
        def get_pdates(col, earliest, latest, missingasongoing=False):
            if col not in cols:
                return None, earliest, latest
            else:
                if pd := hdate.HDate(row[col], missingasongoing=missingasongoing).pdates:
                    earliest = min(pd['early'], earliest) if earliest else pd['early']
                    latest = max(pd['late'], latest) if latest else pd['late']
                return pd, earliest, latest

        pdates_start, earliest, latest = get_pdates("hdate", earliest, latest)
        pdates_end, earliest, latest = get_pdates("hdate_end", earliest, latest)
        if showbirthanddeath:
            pdates_birth, earliest, latest = get_pdates("hdate_birth", earliest, latest)
            pdates_death, earliest, latest = get_pdates("hdate_death", earliest, latest, missingasongoing=True)

        ongoing = pdates_end['slcore'] == 'o' if pdates_end else False
        alive = pdates_death['slcore'] == 'o' if pdates_death else False

        if pdates_start and pdates_start['core']:
            if pdates_end:
                labeldate = pdates_start['core'] + (pdates_end['core'] - pdates_start['core'])/2.0
                if ongoing:
                    hovertext = f"{htext} ({calc_yeartext(pdates_start)}...)"
                else:
                    hovertext = f"{htext} ({calc_yeartext(pdates_start)}-{calc_yeartext(pdates_end)})"
            else:
                labeldate = pdates_start['core']
                hovertext = f"{htext} ({calc_yeartext(pdates_start)})"
        elif pdates_birth and pdates_birth['core']:
            if pdates_death:
                labeldate = pdates_birth['core'] + (pdates_death['core'] - pdates_birth['core'])/2.0
            else:
                labeldate = pdates_birth['core']
        else:
            return False # If we cannot calculate a labeldate the trace cannot be shown

        iline = lo.add_trace(earliest, latest, labeldate, text if showlabel else "")
        y = self.max_y_used + (iline + 1) * rowspacing

        if showlabel:
            add_trace_label(fig, pdate=labeldate, label=text, y=y, hyperlink=hlink)

        # Main part, from hdate to hdate_end
        if pdates_start:
            add_trace_part(fig, pdate_start=pdates_start['early'], pdate_end=pdates_start['late'], 
                        label=text, y=y, color=color, width=1, hovertext=hovertext)
            add_trace_marker(fig, pdate=pdates_start['core'], y=y, color=color,
                            showlegend=showlegend, label=text, 
                            hovertext=hovertext, hyperlink=hlink)
            if pdates_end:
                add_trace_part(fig, pdate_start=pdates_start['late'], 
                            pdate_end=pdates_end['early'], 
                            label=text, y=y, color=color, 
                            hovertext=hovertext, hyperlink=hlink)
                add_trace_part(fig, pdate_start=pdates_end['early'], pdate_end=pdates_end['late'], 
                                label=text, y=y, color=color, width=1, hovertext=hovertext)

                if ongoing:   # Right arrow at end of 'ongoing' period
                    add_trace_marker(fig, pdate=pdates_end['late'], y=y, color=color,
                                symbol='arrow-right',
                                hovertext=hovertext, hyperlink=hlink)
                else:        # Normal marker at end of period
                    add_trace_marker(fig, pdate=pdates_end['core'], y=y, color=color,
                                hovertext=hovertext, hyperlink=hlink)
        
        if showbirthanddeath:
            if pdates_birth:
                hovertext = f"{text} (b. {calc_yeartext(pdates_birth)})"
                endpoint = pdates_start['early'] if pdates_start else \
                            pdates_birth['core'] + (pdates_death['core'] - pdates_birth['core']) / 2.0
                add_trace_part(fig, pdate_start=pdates_birth['late'], 
                                    pdate_end=endpoint, 
                    label=text, y=y, color=color, dash='dot', hovertext=hovertext)
                add_trace_part(fig, pdate_start=pdates_birth['early'], pdate_end=pdates_birth['late'], 
                        label=text, y=y, color=color, width=1, dash='dot', hovertext=hovertext)

            if pdates_death:
                hovertext = f"{text} (b. {calc_yeartext(pdates_birth)})" if alive \
                            else f"{text} (d. {calc_yeartext(pdates_death)})"
                startpoint = pdates_end['late'] if pdates_end else \
                            pdates_start['late'] if pdates_start else \
                            pdates_birth['core'] + (pdates_death['core'] - pdates_birth['core']) / 2.0
                add_trace_part(fig, pdate_start=startpoint, pdate_end=pdates_death['early'], 
                    label=text, y=y, color=color, dash='dot', hovertext=hovertext)
                add_trace_part(fig, pdate_start=max(startpoint,pdates_death['early']), 
                               pdate_end=pdates_death['late'], 
                    label=text, y=y, color=color, width=1, dash='dot', hovertext=hovertext)
                if alive and (pdates_death['late'] > startpoint):   # Right arrow 
                    add_trace_marker(fig, pdate=pdates_death['late'], y=y, color=color,
                                symbol='arrow-right',
                                hovertext=hovertext)
        return True

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
                   color=None, size=10, symbol='diamond', showlegend=False,
                   hovertext=None, hyperlink=None):
    fig.add_trace(go.Scatter(x = [pdate], y=[y], name=label, legendgroup=label,
                        mode="markers", marker={'color':color, 'size':size,'symbol':symbol}, 
                        hoverinfo='text',
                        hovertext=hovertext if hovertext else label,
                        hoverlabel={'namelength':-1}, showlegend=showlegend))

# ------------------------------------------------------------------------------------------------
def add_trace_part(fig, pdate_start=None, pdate_end=None, label="", y=0.0, 
                   color=None, 
                   width=4, dash=None, 
                   hovertext=None, 
                   hyperlink=None):

    if (pdate_start <= pdate_end): 
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
def add_trace_label(fig, pdate=None, label="", y=0.0, hyperlink=None):
    hlinkedtext = f'<a href="{hyperlink}">{label}</a>' if hyperlink else label
    fig.add_trace(go.Scatter(x = [pdate], y=[y+0.04], 
                                name=label, legendgroup=label,
                                mode="text", text=hlinkedtext, 
                                textposition='bottom center',
                                hoverinfo='text', hoverlabel={'namelength':-1}, showlegend=False))
# ------------------------------------------------------------------------------------------------
def calc_yeartext(pdates):
    if pdates['early'].year != pdates['late'].year:
        return f"{pdates['core'].year}?"
    elif pdates['early'].month != pdates['late'].month:
        return f"{pdates['core'].year}"
    elif pdates['early'].day != pdates['late'].day:
        return pdates['core'].strftime("%b %Y")
    else:
        return pdates['core'].strftime("%d %b %Y")
