"""
Plotly timelines for historicaldate package
"""
import sys
sys.path.append("..")

import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly import colors as pc
from historicaldate import hdate
from historicaldate import lineorganiser
from dateutil.relativedelta import relativedelta
from math import ceil

class plTimeLine():
    def __init__(self, title=None, mindate=None, maxdate=None, 
                hovermode='closest', hoverdistance=5):
        self.figure = make_subplots(rows=1, cols=1, subplot_titles=[title])
        self.figure.update_layout(xaxis_title=None, title=None, margin={'l':0,'r':0,'t':20,'b':0})
        self.maxdate = datetime.date.today() + datetime.timedelta(days=int(10*365.25)) \
                            if maxdate is None else maxdate
        self.mindate = self.maxdate - datetime.timedelta(days=int(200*365.25)) \
                            if mindate is None else mindate
        self.pointinterval = (self.maxdate - self.mindate) / 200.0
        self.initial_range_years = (self.maxdate - self.mindate).days / 365.

        self.fig_config = {'scrollZoom': True}
        self.figure.update_layout(dragmode="pan", showlegend=False, 
                    hovermode=hovermode, hoverdistance=hoverdistance)
        self.figure.update_xaxes(range=[self.mindate, self.maxdate])
        self.max_y_used = 0.0
# -------------
    def add_event_set(self, df, 
                    title="", showbirthanddeath=True, showlabel=True,
                    lives_first=True,  rowspacing=0.3, hover_datetype='day'):
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
            df["_hdplsortorder"] = df["hdate"].apply(hdate.calc_mid_date)
            dfs = df.sort_values("_hdplsortorder")
        else:
            dfs = df

        lo = lineorganiser.LineOrganiser(daysperlabelchar=2.5 * self.initial_range_years,
                                         daysminspacing=0.5 * self.initial_range_years)

        def disp_set(dfset):
            for _, row in dfset.iterrows():  
                color = row[colorcol] if colorcol and row[colorcol] else colorgen.get()
                self.add_timeline_trace(row, 
                                showbirthanddeath=showbirthanddeath, showlabel=showlabel,
                                color=color, lo=lo, hover_datetype=hover_datetype)

        # -- split lives and display them first if required
        if "hdate_birth" in dfs.columns and lives_first:
            dfs["_hdplbirth"] = dfs["hdate_birth"].apply(hdate.calc_mid_date)
            df_lives = dfs[dfs["_hdplbirth"].notna()].sort_values(["_hdplbirth"])
            disp_set(df_lives)
            dfs = dfs[dfs["_hdplbirth"].isna()]
            lo.reset_startline()

        disp_set(dfs)
        self.max_y_used += (len(lo.linerecord) + 2) * rowspacing    
# -------------
    def add_timeline_trace(self, row, showbirthanddeath=False, 
                                    showlegend=True, showlabel=True,
                                    color=None, lo=None, rowspacing=0.3,
                                    hover_datetype='day'):
        '''
        Add a timeline trace for a given row
        '''        
        fig = self.figure
        cols = list(row.index)
        text = row["label"]
        htext = row["description"] if "description" in cols and row["description"] else text
        htext_end = row["htext_end"] if "htext_end" in cols and row["htext_end"] else htext
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
            pdates_death, earliest, latest = get_pdates("hdate_death", earliest, latest, 
                        missingasongoing=pdates_birth and pdates_birth['mid'])

        ongoing = pdates_end['slmid'] == 'o' if pdates_end else False
        alive = pdates_death['slmid'] == 'o' if pdates_death else False

        hovertext_end = None
        if pdates_start and pdates_start['mid']:
            if pdates_end:
                labeldate = pdates_start['mid'] + (pdates_end['mid'] - pdates_start['mid'])/2.0
                if ongoing:
                    hovertext = f"{htext} ({calc_yeartext(pdates_start, hover_datetype=hover_datetype)}...)"
                else:
                    hovertext = f"{htext} ({calc_yeartext(pdates_start, hover_datetype=hover_datetype)}-"\
                                        f"{calc_yeartext(pdates_end, hover_datetype=hover_datetype)})"
                    if htext_end != htext:
                        hovertext_end = f"{htext_end} ({calc_yeartext(pdates_end, hover_datetype='day')})"
            else:
                labeldate = pdates_start['mid']
                hovertext = f"{htext} ({calc_yeartext(pdates_start, hover_datetype=hover_datetype)})"
        elif pdates_birth and pdates_birth['mid']:
            if pdates_death:
                labeldate = pdates_birth['mid'] + (pdates_death['mid'] - pdates_birth['mid'])/2.0
            else:
                labeldate = pdates_birth['mid']
        else:
            return False # If we cannot calculate a labeldate the trace cannot be shown

        iline = lo.add_trace(earliest, latest, labeldate, text if showlabel else "")
        y = self.max_y_used + (iline + 1) * rowspacing

        if showlabel:
            add_trace_label(fig, pdate=labeldate, label=text, y=y, hyperlink=hlink)

        # Main part, from hdate to hdate_end
        if pdates_start:
            self.add_trace_part(pdate_start=pdates_start['early'], pdate_end=pdates_start['late'], 
                        label=text, y=y, color=color, width=1, hovertext=hovertext)
            add_trace_marker(fig, pdate=pdates_start['mid'], y=y, color=color,
                            showlegend=showlegend, label=text, 
                            hovertext=hovertext, hyperlink=hlink)
            if pdates_end:
                self.add_trace_part(pdate_start=pdates_start['late'], 
                            pdate_end=pdates_end['early'], 
                            label=text, y=y, color=color, 
                            hovertext=hovertext, hovertext_end=hovertext_end)
                self.add_trace_part(pdate_start=pdates_end['early'], pdate_end=pdates_end['late'], 
                                label=text, y=y, color=color, width=1, 
                                hovertext=hovertext, hovertext_end=hovertext_end)

                if ongoing:   # Right arrow at end of 'ongoing' period
                    add_trace_marker(fig, pdate=pdates_end['late'], y=y, color=color,
                                symbol='arrow-right',
                                hovertext=hovertext, hyperlink=hlink)
                else:        # Normal marker at end of period
                    add_trace_marker(fig, pdate=pdates_end['mid'], y=y, color=color,
                                hovertext=hovertext_end if hovertext_end else hovertext, 
                                hyperlink=hlink)
        
        if showbirthanddeath:
            if pdates_birth and pdates_birth['mid']:
                hovertext = f"{htext} (b. {calc_yeartext(pdates_birth, hover_datetype=hover_datetype)})"
                endpoint = pdates_start['early'] if pdates_start else \
                            pdates_birth['mid'] + (pdates_death['mid'] - pdates_birth['mid']) / 2.0
                self.add_trace_part(pdate_start=pdates_birth['late'], 
                                    pdate_end=endpoint, 
                    label=text, y=y, color=color, dash='dot', hovertext=hovertext)
                if pdates_birth['early'] < pdates_birth['late']:
                    self.add_trace_part(pdate_start=pdates_birth['early'], pdate_end=pdates_birth['late'], 
                        label=text, y=y, color=color, width=1, dash='dot', hovertext=hovertext)

            if pdates_death and pdates_death['mid']:
                hovertext = f"{htext} (b. {calc_yeartext(pdates_birth, hover_datetype=hover_datetype)})" if alive \
                            else f"{htext} (d. {calc_yeartext(pdates_death, hover_datetype=hover_datetype)}" +\
                                    f" aged {calc_agetext(pdates_birth, pdates_death)})"
                startpoint = pdates_end['late'] if pdates_end else \
                            pdates_start['late'] if pdates_start else \
                            pdates_birth['mid'] + (pdates_death['mid'] - pdates_birth['mid']) / 2.0
                self.add_trace_part(pdate_start=startpoint, pdate_end=pdates_death['early'], 
                    label=text, y=y, color=color, dash='dot', hovertext=hovertext)
                if pdates_death['early'] < pdates_death['late']:
                    self.add_trace_part(pdate_start=max(startpoint,pdates_death['early']), 
                               pdate_end=pdates_death['late'], 
                    label=text, y=y, color=color, width=1, dash='dot', hovertext=hovertext)
                if alive and (pdates_death['late'] > startpoint):   # Right arrow 
                    add_trace_marker(fig, pdate=pdates_death['late'], y=y, color=color,
                                symbol='arrow-right',
                                hovertext=hovertext)
        return True
# -------------
    def add_trace_part(self, pdate_start=None, pdate_end=None, label="", y=0.0, 
                    color=None, width=4, dash=None, 
                    hovertext=None, hovertext_end=None):

        if hovertext_end is None:
            hovertext_end = hovertext

        if (pdate_start <= pdate_end): 
            #xs = [pdate_start] + \
            #     [datetime.date(year, 1, 1) for year in 
            #            range(pdate_start.year + 1, pdate_end.year + 1)] + [pdate_end]
            xs = [pdate_start + n * self.pointinterval for n in 
                        range(ceil((pdate_end - pdate_start).total_seconds()/
                                    self.pointinterval.total_seconds()))] + [pdate_end]
            ys = [y for _ in xs]
            hovertexts = label if not hovertext \
                            else hovertext if hovertext == hovertext_end \
                            else [hovertext for _ in range(len(xs) - 1)] + [hovertext_end]
            self.figure.add_trace(go.Scatter(x = xs, y=ys, name=label, legendgroup=label,
                                mode="lines", line={'color':color,'width':width,'dash':dash}, 
                                hoverinfo='text',
                                hovertext=hovertexts,
                                hoverlabel={'namelength':-1}, showlegend=False))

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
                   color=None, size=8, symbol='diamond', showlegend=False,
                   hovertext=None, hyperlink=None):
    fig.add_trace(go.Scatter(x = [pdate], y=[y], name=label, legendgroup=label,
                        mode="markers", marker={'color':color, 'size':size,'symbol':symbol}, 
                        hoverinfo='text',
                        hovertext=hovertext if hovertext else label,
                        hoverlabel={'namelength':-1}, showlegend=showlegend))
# ------------------------------------------------------------------------------------------------
def add_trace_label(fig, pdate=None, label="", y=0.0, hyperlink=None):
    hlinkedtext = f'<a href="{hyperlink}">{label}</a>' if hyperlink else label
    fig.add_trace(go.Scatter(x = [pdate], y=[y+0.04], 
                                name=label, legendgroup=label,
                                mode="text", text=hlinkedtext, 
                                textposition='bottom center',
                                hoverinfo='skip', hoverlabel={'namelength':-1}, showlegend=False))
# ------------------------------------------------------------------------------------------------
def calc_yeartext(pdates, hover_datetype='day'):
    if hover_datetype not in {'year','month','day'}:
        raise ValueError(f"hover_datetype must be year, month or day. found:{hover_datetype}")
    
    if (pdates['early'].year != pdates['late'].year):
        return f"{pdates['mid'].year}?"             # Show uncertain year
    elif (pdates['early'].month != pdates['late'].month) or hover_datetype in {'year'}:
        return f"{pdates['mid'].year}"              # Show year
    elif (pdates['early'].day != pdates['late'].day) or hover_datetype in {'year','month'}:
        return pdates['mid'].strftime("%b %Y")      # Show month and year
    else:
        return pdates['mid'].strftime("%d %b %Y")   # Show exact date
# ------------------------------------------------------------------------------------------------    
def calc_agetext(pdates_birth, pdates_ref):
    "Calculate age text, including ? to indicate uncertainty"
    years_largest = relativedelta(pdates_ref['late'],pdates_birth['early']).years
    years_smallest = relativedelta(pdates_ref['early'],pdates_birth['late']).years
    uncertain = '?' if years_largest > years_smallest else ""

    years = relativedelta(pdates_ref['mid'],pdates_birth['mid']).years
    return f"{years}{uncertain}"
