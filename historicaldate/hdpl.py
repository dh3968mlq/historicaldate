"""
Plotly timelines for historicaldate package
"""
import sys
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly import colors as pc
from dateutil.relativedelta import relativedelta
from math import ceil

try:
    import historicaldate.hdate as hdate
except:
    import historicaldate.historicaldate.hdate as hdate

try:
    import historicaldate.lineorganiser as lineorganiser
except:
    import historicaldate.historicaldate.lineorganiser as lineorganiser

class plTimeLine():
    def __init__(self, title=None, mindate=None, maxdate=None, 
                hovermode='closest', hoverdistance=5, xmode="date"):
        """
        To do... When calling this, mindate and maxdate may be either int (ordinal days) or dates
        self.mindate, self.maxdate always stored as ordinals
        """
        if xmode not in {"date","years"}:
            raise ValueError(f"xmode must be 'date' or 'years', not '{xmode}'")
        
        self._xmode = xmode
        self.figure = make_subplots(rows=1, cols=1, subplot_titles=[title])
        self.figure.update_layout(xaxis_title=None, title=None, margin={'l':0,'r':0,'t':20,'b':0})
        self.maxdate = hdate.to_ordinal(datetime.date.today(), delta=int(10*365.25)) \
                        if maxdate is None else hdate.to_ordinal(maxdate)
        self.mindate = hdate.to_ordinal(self.maxdate, delta= -int(200*365.25)) \
                            if mindate is None else hdate.to_ordinal(mindate)
        self.pointinterval = int((self.maxdate - self.mindate) / 200.0)
        self.initial_range_years = (self.maxdate - self.mindate) / 365.

        self.fig_config = {'scrollZoom': True}
        self.figure.update_layout(dragmode="pan", showlegend=False, 
                    hovermode=hovermode, hoverdistance=hoverdistance)
        self.max_y_used = 0.0
        self.earliest_trace_date = None
        self.latest_trace_date = None
        self.fit_xaxis()

# -------------
    def fit_xaxis(self, mindate=None, maxdate=None):
        """
        Fit x axis to specified dates, or to data range
        mindate and maxdate may be either ordinals (int) or Python dates
        """
        minord = hdate.to_ordinal(mindate)
        maxord = hdate.to_ordinal(maxdate)

        earliest = minord if minord is not None \
                        else self.earliest_trace_date - int(5*365.25) if self.earliest_trace_date is not None \
                        else self.mindate
        latest = maxord if maxord is not None \
                        else self.latest_trace_date + int(5*365.25) if self.latest_trace_date is not None \
                        else self.maxdate
        if fitted := earliest and latest and (latest > earliest):
            self.maxdate = latest 
            self.mindate = earliest 
            if self._xmode == "date":
                self.figure.update_xaxes(range=[hdate.to_python_date(self.mindate), 
                                            hdate.to_python_date(self.maxdate)], side="top")
            else:
                self.figure.update_xaxes(range=[hdate.to_years(self.mindate), 
                                            hdate.to_years(self.maxdate)], side="top")
        return fitted 
# -------------
    def add_event_set(self, df, 
                    title="", showbirthanddeath=True, showlabel=True,
                    lives_first=True,  rowspacing=0.3, hover_datetype='day',
                    study_range_start=None, study_range_end=None,
                    max_rank=1):
        """
        dates are in df columns: hdate, hdate_end, hdate_birth, hdate_death
        df must include either hdate or both of hdate_birth, hdate_death

        Other columns:
            label: String label or identifier (required)
            text: Hovertext (optional, defaults to label)
            url: hyperlink (optional)

        At present study_range_start and study_range_end are Python dates, this will need changing
        """
        colorgen = ColorGen()
        colorcol = "color" if "color" in df.columns \
                    else "colour" if "colour" in df.columns \
                    else ""

        if "hdate" in df.columns:
            df["_hdplsortorder"] = df["hdate"].apply(hdate.calc_mid_ordinal)
            dfs = df.sort_values("_hdplsortorder")
        elif "hdate_birth" in df.columns:
            df["_hdplsortorder"] = df["hdate_birth"].apply(hdate.calc_mid_ordinal)
            dfs = df.sort_values("_hdplsortorder") 
        else:
            dfs = df

        if "rank" in dfs.columns:
            dfs = dfs[dfs["rank"] <= max_rank]

        lo = lineorganiser.LineOrganiser(daysperlabelchar=2.5 * self.initial_range_years,
                                         daysminspacing=0.5 * self.initial_range_years)

        def disp_set(dfset):
            some_traces_added = False
            for _, row in dfset.iterrows():  
                color = row[colorcol] if colorcol and row[colorcol] else colorgen.get()
                some_traces_added = self.add_timeline_trace(row, 
                                showbirthanddeath=showbirthanddeath, showlabel=showlabel,
                                color=color, lo=lo, hover_datetype=hover_datetype,
                                study_range_start=study_range_start, 
                                study_range_end=study_range_end) or \
                            some_traces_added
            return some_traces_added

        # -- split lives and display them first if required
        some_events_added = False
        if "hdate_birth" in dfs.columns and lives_first:
            dfs["_hdplbirth"] = dfs["hdate_birth"].apply(hdate.calc_mid_ordinal)
            df_lives = dfs[dfs["_hdplbirth"].notna()].sort_values(["_hdplbirth"])
            some_events_added = disp_set(df_lives) or some_events_added
            dfs = dfs[dfs["_hdplbirth"].isna()]   # -- not lives
            lo.reset_startline()

        some_events_added = disp_set(dfs) or some_events_added 

        # The event set is ignored if it lies entirely outside the study range
        if some_events_added:
            if title:
                self.figure.add_annotation(text=f"<b>{title}</b>", 
                        x=0.02, xref='paper', y=self.max_y_used, 
                        showarrow=False, font={'size':14})

            self.max_y_used += (len(lo.linerecord) + 2) * rowspacing
            self.figure.update_yaxes(range=[max(self.max_y_used+0.25,6.0),-0.25], 
                                    visible=False)
        return some_events_added
 
# -------------
    def add_timeline_trace(self, row, showbirthanddeath=False, 
                        showlegend=True, showlabel=True,
                        color=None, lo=None, rowspacing=0.3,
                        hover_datetype='day',
                        study_range_start=None, study_range_end=None):
        '''
        Add a timeline trace for a given row

        At present study_range_start and study_range_end are Python dates, this will need changing
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
                    earliest = min(pd['ordinal_early'], earliest) if earliest is not None else pd['ordinal_early']
                    latest = max(pd['ordinal_late'], latest) if latest is not None else pd['ordinal_late']
                return pd, earliest, latest

        pdates_start, earliest, latest = get_pdates("hdate", earliest, latest)
        pdates_end, earliest, latest = get_pdates("hdate_end", earliest, latest)
        if showbirthanddeath:
            pdates_birth, earliest, latest = get_pdates("hdate_birth", earliest, latest)
            pdates_death, earliest, latest = get_pdates("hdate_death", earliest, latest, 
                        missingasongoing=pdates_birth and (pdates_birth['ordinal_mid'] is not None))
        
        if study_range_start and study_range_end:
            if latest < (study_range_start - datetime.date(1, 1, 1)).days or \
                earliest > (study_range_end - datetime.date(1, 1, 1)).days:
                # Trace is outside study range, ignore it
                return False

        ongoing = pdates_end['slmid'] == 'o' if pdates_end else False
        alive = pdates_death['slmid'] == 'o' if pdates_death else False

        hovertext_end = None
        if pdates_start and (pdates_start['ordinal_mid'] is not None):
            if pdates_end:
                labeldate = pdates_start['ordinal_mid'] + int((pdates_end['ordinal_mid'] - pdates_start['ordinal_mid'])/2.0)
                if ongoing:
                    hovertext = f"{htext} ({calc_yeartext(pdates_start, hover_datetype=hover_datetype)}...)"
                else:
                    hovertext = f"{htext} ({calc_yeartext(pdates_start, hover_datetype=hover_datetype)}-"\
                                        f"{calc_yeartext(pdates_end, hover_datetype=hover_datetype)})"
                    if htext_end != htext:
                        hovertext_end = f"{htext_end} ({calc_yeartext(pdates_end, hover_datetype='day')})"
            else:
                labeldate = pdates_start['ordinal_mid']
                hovertext = f"{htext} ({calc_yeartext(pdates_start, hover_datetype=hover_datetype)})"
        elif pdates_birth and (pdates_birth['ordinal_mid'] is not None):
            if pdates_death:
                labeldate = pdates_birth['ordinal_mid'] + int((pdates_death['ordinal_mid'] - pdates_birth['ordinal_mid'])/2.0)
            else:
                labeldate = pdates_birth['ordinal_mid']
        else:
            return False # If we cannot calculate a labeldate the trace cannot be shown

        # Decide what line to draw it on
        iline = lo.add_trace(earliest, latest, labeldate, text if showlabel else "")
        y = self.max_y_used + (iline + 1) * rowspacing

        # -- Update timeline object earliest / latest trace dates
        self.earliest_trace_date = min(self.earliest_trace_date, earliest) if self.earliest_trace_date is not None else earliest
        self.latest_trace_date = max(self.latest_trace_date, latest) if self.latest_trace_date is not None else latest

        if showlabel:
            add_trace_label(fig, pdate=labeldate, label=text, y=y, hyperlink=hlink, xmode=self._xmode)

        # Main part, from hdate to hdate_end
        if pdates_start:
            self.add_trace_part(pdate_start=pdates_start['ordinal_early'], pdate_end=pdates_start['ordinal_late'], 
                        label=text, y=y, color=color, width=1, hovertext=hovertext)
            add_trace_marker(fig, pdate=pdates_start['ordinal_mid'], y=y, color=color,
                            showlegend=showlegend, label=text, 
                            hovertext=hovertext, hyperlink=hlink, xmode=self._xmode)
            if pdates_end:
                self.add_trace_part(pdate_start=pdates_start['ordinal_late'], 
                            pdate_end=pdates_end['ordinal_early'], 
                            label=text, y=y, color=color, 
                            hovertext=hovertext, hovertext_end=hovertext_end)
                self.add_trace_part(pdate_start=pdates_end['ordinal_early'], pdate_end=pdates_end['ordinal_late'], 
                                label=text, y=y, color=color, width=1, 
                                hovertext=hovertext, hovertext_end=hovertext_end)

                if ongoing:   # Right arrow at end of 'ongoing' period
                    add_trace_marker(fig, pdate=pdates_end['ordinal_late'], y=y, color=color,
                                symbol='arrow-right',
                                hovertext=hovertext, hyperlink=hlink, xmode=self._xmode)
                else:        # Normal marker at end of period
                    add_trace_marker(fig, pdate=pdates_end['ordinal_mid'], y=y, color=color,
                                hovertext=hovertext_end if hovertext_end else hovertext, 
                                hyperlink=hlink, xmode=self._xmode)
        
        if showbirthanddeath:
            if pdates_birth and pdates_birth['ordinal_mid']:
                hovertext = f"{htext} (b. {calc_yeartext(pdates_birth, hover_datetype=hover_datetype)})"
                endpoint = pdates_start['ordinal_early'] if pdates_start else \
                            pdates_birth['ordinal_mid'] + int((pdates_death['ordinal_mid'] - pdates_birth['ordinal_mid']) / 2.0)
                self.add_trace_part(pdate_start=pdates_birth['ordinal_late'], 
                                    pdate_end=endpoint, 
                    label=text, y=y, color=color, dash='dot', hovertext=hovertext)
                if pdates_birth['ordinal_early'] < pdates_birth['ordinal_late']:
                    self.add_trace_part(pdate_start=pdates_birth['ordinal_early'], pdate_end=pdates_birth['ordinal_late'], 
                        label=text, y=y, color=color, width=1, dash='dot', hovertext=hovertext)

            if pdates_death and (pdates_death['ordinal_mid'] is not None):
                hovertext = f"{htext} (b. {calc_yeartext(pdates_birth, hover_datetype=hover_datetype)})" if alive \
                            else f"{htext} (d. {calc_yeartext(pdates_death, hover_datetype=hover_datetype)}" +\
                                    f" aged {calc_agetext(pdates_birth, pdates_death)})"
                startpoint = pdates_end['ordinal_late'] if pdates_end else \
                            pdates_start['ordinal_late'] if pdates_start else \
                            pdates_birth['ordinal_mid'] + int((pdates_death['ordinal_mid'] - pdates_birth['ordinal_mid']) / 2.0)
                self.add_trace_part(pdate_start=startpoint, pdate_end=pdates_death['ordinal_early'], 
                    label=text, y=y, color=color, dash='dot', hovertext=hovertext)
                if pdates_death['ordinal_early'] < pdates_death['ordinal_late']:
                    self.add_trace_part(pdate_start=max(startpoint,pdates_death['ordinal_early']), 
                               pdate_end=pdates_death['ordinal_late'], 
                    label=text, y=y, color=color, width=1, dash='dot', hovertext=hovertext)
                if alive and (pdates_death['ordinal_late'] > startpoint):   # Right arrow 
                    add_trace_marker(fig, pdate=pdates_death['ordinal_late'], y=y, color=color,
                                symbol='arrow-right',
                                hovertext=hovertext, xmode=self._xmode)
        return True
# -------------
    def add_trace_part(self, pdate_start=None, pdate_end=None, label="", y=0.0, 
                    color=None, width=4, dash=None, 
                    hovertext=None, hovertext_end=None):

        if hovertext_end is None:
            hovertext_end = hovertext

        if (pdate_start <= pdate_end): 
            if self._xmode == "date":
                pointinterval = datetime.timedelta(days=self.pointinterval)
                xs = [hdate.to_python_date(pdate_start) + n * pointinterval for n in 
                    range(ceil((hdate.to_python_date(pdate_end) - hdate.to_python_date(pdate_start)).total_seconds()/
                                    pointinterval.total_seconds()))] + [hdate.to_python_date(pdate_end)]
            else:
                xs = [hdate.to_years(hdate.to_ordinal(pdate_start) + n * self.pointinterval) for n in 
                        range(ceil((hdate.to_ordinal(pdate_end) - hdate.to_ordinal(pdate_start))/
                                    self.pointinterval))] + [hdate.to_years(pdate_end)]
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
                   hovertext=None, hyperlink=None, xmode="date"):
    pltdate = hdate.to_python_date(pdate) if xmode == "date" else hdate.to_years(pdate)
    fig.add_trace(go.Scatter(x = [pltdate], y=[y], name=label, legendgroup=label,
                        mode="markers", marker={'color':color, 'size':size,'symbol':symbol}, 
                        hoverinfo='text',
                        hovertext=hovertext if hovertext else label,
                        hoverlabel={'namelength':-1}, showlegend=showlegend))
# ------------------------------------------------------------------------------------------------
def add_trace_label(fig, pdate=None, label="", y=0.0, hyperlink=None, xmode="date"):
    hlinkedtext = f'<a href="{hyperlink}">{label}</a>' if hyperlink else label
    pltdate = hdate.to_python_date(pdate) if xmode == "date" else hdate.to_years(pdate)
    fig.add_trace(go.Scatter(x = [pltdate], y=[y+0.04], 
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
