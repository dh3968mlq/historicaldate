import sys
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly import colors as pc
from dateutil.relativedelta import relativedelta
from math import ceil

try:
    import historicaldate.hdate as hdate
    import historicaldate.hdateutils as hdateutils
    import historicaldate.lineorganiser as lineorganiser
    import historicaldate.colorgen as colorgen
except:
    import historicaldate.historicaldate.hdate as hdate
    import historicaldate.historicaldate.hdateutils as hdateutils
    import historicaldate.historicaldate.lineorganiser as lineorganiser
    import historicaldate.historicaldate.colorgen as colorgen

try:
    import historicaldate.hdplutils as hdplutils
except:
    import historicaldate.historicaldate.hdplutils as hdplutils

def check_dataframe(df, study_range_start=None, study_range_end=None, dateformat="default"):
    pltl = plTimeLine(mindate="2000 BC", maxdate="2200", xmode="years", dateformat=dateformat)
    message = ""
    try:
        added = pltl.add_event_set(df, study_range_start=study_range_start, study_range_end=study_range_end)
        if not added:
            message = "No events found in study range"
    except Exception as e:
        added = False
        message = f"Error: {repr(e)}"
    return added, message

class plTimeLine():
    def __init__(self, title=None, mindate=None, maxdate=None, 
                hovermode='closest', hoverdistance=5, xmode="date", dateformat=None):
        """
        To do... When calling this, mindate and maxdate may be either int (ordinal days) or dates
        self.mindate, self.maxdate always stored as ordinals
        """
        if xmode not in {"date","years"}:
            raise ValueError(f"xmode must be 'date' or 'years', not '{xmode}'")
        
        dateformat_valid = {None, "default", "mdy", "dmy"}
        if dateformat not in dateformat_valid:
            raise ValueError(f"dateformat must be in {dateformat_valid}, not '{dateformat}'")

        self._xmode = xmode
        self._dateformat = None if dateformat == "default" else dateformat

        self.figure = make_subplots(rows=1, cols=1, subplot_titles=[title])
        self.figure.update_annotations(y=1.015, yref="paper", selector={'text':title})
        self.figure.update_layout(xaxis_title=None, title=None, margin={'l':0,'r':0,'t':40,'b':0})
        self.maxdate = hdateutils.to_ordinal(datetime.date.today(), delta=int(10*365.25)) \
                        if maxdate is None else hdateutils.to_ordinal(maxdate)
        self.mindate = hdateutils.to_ordinal(self.maxdate, delta= -int(200*365.25)) \
                            if mindate is None else hdateutils.to_ordinal(mindate)
        self.pointinterval = int((self.maxdate - self.mindate) / 200.0)
        self.initial_range_years = (self.maxdate - self.mindate) / 365.

        self.fig_config = {'scrollZoom': True}
        self.figure.update_layout(dragmode="pan", showlegend=False, 
                    hovermode=hovermode, hoverdistance=hoverdistance)
        self.max_y_used = 0.0
        self.fit_xaxis()

# -------------
    def fit_xaxis(self, mindate=None, maxdate=None):
        """
        Fit x axis to specified dates, or to data range
        mindate and maxdate may be either ordinals (int) or Python dates
        """
        minord = hdateutils.to_ordinal(mindate, dateformat=self._dateformat)
        maxord = hdateutils.to_ordinal(maxdate, dateformat=self._dateformat)

        earliest = minord if minord is not None \
                        else self.mindate
        latest = maxord if maxord is not None \
                        else self.maxdate
        if fitted := earliest and latest and (latest > earliest):
            self.maxdate = latest 
            self.mindate = earliest 
            if self._xmode == "date":
                self.figure.update_xaxes(range=[hdateutils.to_python_date(self.mindate), 
                                            hdateutils.to_python_date(self.maxdate)], side="top")
            else:
                self.figure.update_xaxes(range=[hdateutils.to_years(self.mindate), 
                                            hdateutils.to_years(self.maxdate)], side="top")
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

        study_range_start, study_range_end may be either Python dates or ordinals
        """
        cgen = colorgen.ColorGen()
        colorcol = "color" if "color" in df.columns \
                    else "colour" if "colour" in df.columns \
                    else ""

        if "hdate" in df.columns:
            df["_hdplsortorder"] = df["hdate"].apply(lambda x: hdateutils.calc_mid_ordinal(x, dateformat=self._dateformat))
            dfs = df.sort_values("_hdplsortorder")
        elif "hdate_birth" in df.columns:
            df["_hdplsortorder"] = df["hdate_birth"].apply(lambda x: hdateutils.calc_mid_ordinal(x, dateformat=self._dateformat))
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
                color = row[colorcol] if colorcol and row[colorcol] else cgen.get()
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
            dfs["_hdplbirth"] = dfs["hdate_birth"].apply(lambda x: hdateutils.calc_mid_ordinal(x, dateformat=self._dateformat))
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
    def add_timeline_trace(self, row, showbirthanddeath=False, 
                        showlegend=True, showlabel=True,
                        color=None, lo=None, rowspacing=0.3,
                        hover_datetype='day',
                        study_range_start=None, study_range_end=None):
        '''
        Add a timeline trace for a given row
        study_range start, study_range_end may be either python dates or ordinals
        '''        
        fig = self.figure
        cols = list(row.index)
        text = row["label"]
        htext = row["description"] if "description" in cols and row["description"] else text
        htext_end = row["htext_end"] if "htext_end" in cols and row["htext_end"] else htext
        hlink = row['url'] if 'url' in cols else None

        study_ordinal_start = hdateutils.to_ordinal(study_range_start, dateformat=self._dateformat)
        study_ordinal_end = hdateutils.to_ordinal(study_range_end, dateformat=self._dateformat)

        earliest, latest = None, None

        # Function to get a date
        def get_pdates(col, earliest, latest, missingasongoing=False):
            if col not in cols:
                return None, earliest, latest
            else:
                if pd := hdate.HDate(row[col], missingasongoing=missingasongoing, dateformat=self._dateformat).pdates:
                    earliest = min(pd['ordinal_early'], earliest) if earliest is not None else pd['ordinal_early']
                    latest = max(pd['ordinal_late'], latest) if latest is not None else pd['ordinal_late']
                return pd, earliest, latest

        pdates_start, earliest, latest = get_pdates("hdate", earliest, latest)
        pdates_end, earliest, latest = get_pdates("hdate_end", earliest, latest)
        if showbirthanddeath:
            pdates_birth, earliest, latest = get_pdates("hdate_birth", earliest, latest)
            pdates_death, earliest, latest = get_pdates("hdate_death", earliest, latest, 
                        missingasongoing=pdates_birth and (pdates_birth['ordinal_mid'] is not None))
        
        if (study_ordinal_start is not None) and (study_ordinal_end is not None):
            if latest < study_ordinal_start or earliest > study_ordinal_end:
                # Trace is outside study range, ignore it
                return False

        ongoing = pdates_end['slmid'] == 'o' if pdates_end else False
        alive = pdates_death['slmid'] == 'o' if pdates_death else False

        hovertext_end = None
        if pdates_start and (pdates_start['ordinal_mid'] is not None):
            if pdates_end:
                labeldate = pdates_start['ordinal_mid'] + int((pdates_end['ordinal_mid'] - pdates_start['ordinal_mid'])/2.0)
                if ongoing:
                    hovertext = f"{htext} ({hdplutils.calc_yeartext(pdates_start, hover_datetype=hover_datetype)}...)"
                else:
                    hovertext = f"{htext} ({hdplutils.calc_yeartext(pdates_start, hover_datetype=hover_datetype)}-"\
                                        f"{hdplutils.calc_yeartext(pdates_end, hover_datetype=hover_datetype)})"
                    if htext_end != htext:
                        hovertext_end = f"{htext_end} ({hdplutils.calc_yeartext(pdates_end, hover_datetype='day')})"
            else:
                labeldate = pdates_start['ordinal_mid']
                hovertext = f"{htext} ({hdplutils.calc_yeartext(pdates_start, hover_datetype=hover_datetype)})"
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

        if showlabel:
            hdplutils.add_trace_label(fig, pdate=labeldate, label=text, y=y, hyperlink=hlink, xmode=self._xmode)

        # Main part, from hdate to hdate_end
        if pdates_start:
            hdplutils.add_trace_part(self.figure, 
                        pdate_start=pdates_start['ordinal_early'], pdate_end=pdates_start['ordinal_late'], 
                        label=text, y=y, color=color, width=1, hovertext=hovertext,
                        xmode=self._xmode, dateformat=self._dateformat, pointinterval=self.pointinterval
                        )
            hdplutils.add_trace_marker(fig, pdate=pdates_start['ordinal_mid'], y=y, color=color,
                            showlegend=showlegend, label=text, 
                            hovertext=hovertext, hyperlink=hlink, xmode=self._xmode)
            if pdates_end:
                hdplutils.add_trace_part(self.figure, 
                            pdate_start=pdates_start['ordinal_late'], 
                            pdate_end=pdates_end['ordinal_early'], 
                            label=text, y=y, color=color, 
                            hovertext=hovertext, hovertext_end=hovertext_end,
                            xmode=self._xmode, dateformat=self._dateformat, pointinterval=self.pointinterval
                        )
                hdplutils.add_trace_part(self.figure, 
                            pdate_start=pdates_end['ordinal_early'], pdate_end=pdates_end['ordinal_late'], 
                                label=text, y=y, color=color, width=1, 
                                hovertext=hovertext, hovertext_end=hovertext_end,
                        xmode=self._xmode, dateformat=self._dateformat, pointinterval=self.pointinterval
                        )

                if ongoing:   # Right arrow at end of 'ongoing' period
                    hdplutils.add_trace_marker(fig, pdate=pdates_end['ordinal_late'], y=y, color=color,
                                symbol='arrow-right',
                                hovertext=hovertext, hyperlink=hlink, xmode=self._xmode)
                else:        # Normal marker at end of period
                    hdplutils.add_trace_marker(fig, pdate=pdates_end['ordinal_mid'], y=y, color=color,
                                hovertext=hovertext_end if hovertext_end else hovertext, 
                                hyperlink=hlink, xmode=self._xmode)
        
        if showbirthanddeath:
            if pdates_birth and pdates_birth['ordinal_mid']:
                hovertext = f"{htext} (b. {hdplutils.calc_yeartext(pdates_birth, hover_datetype=hover_datetype)})"
                endpoint = pdates_start['ordinal_early'] if pdates_start else \
                            pdates_birth['ordinal_mid'] + int((pdates_death['ordinal_mid'] - pdates_birth['ordinal_mid']) / 2.0)
                hdplutils.add_trace_part(self.figure, 
                                pdate_start=pdates_birth['ordinal_late'], 
                                pdate_end=endpoint, 
                                label=text, y=y, color=color, dash='dot', hovertext=hovertext,
                                xmode=self._xmode, dateformat=self._dateformat, pointinterval=self.pointinterval
                                )
                if pdates_birth['ordinal_early'] < pdates_birth['ordinal_late']:
                    hdplutils.add_trace_part(self.figure, 
                                pdate_start=pdates_birth['ordinal_early'], pdate_end=pdates_birth['ordinal_late'], 
                                label=text, y=y, color=color, width=1, dash='dot', hovertext=hovertext,
                                xmode=self._xmode, dateformat=self._dateformat, pointinterval=self.pointinterval
                                )

            if pdates_death and (pdates_death['ordinal_mid'] is not None):
                hovertext = f"{htext} (b. {hdplutils.calc_yeartext(pdates_birth, hover_datetype=hover_datetype)})" if alive \
                            else f"{htext} (d. {hdplutils.calc_yeartext(pdates_death, hover_datetype=hover_datetype)}" +\
                                    f" aged {hdplutils.calc_agetext(pdates_birth, pdates_death)})"
                startpoint = pdates_end['ordinal_late'] if pdates_end else \
                            pdates_start['ordinal_late'] if pdates_start else \
                            pdates_birth['ordinal_mid'] + int((pdates_death['ordinal_mid'] - pdates_birth['ordinal_mid']) / 2.0)
                hdplutils.add_trace_part(self.figure, 
                            pdate_start=startpoint, pdate_end=pdates_death['ordinal_early'], 
                            label=text, y=y, color=color, dash='dot', hovertext=hovertext,
                            xmode=self._xmode, dateformat=self._dateformat, pointinterval=self.pointinterval
                            )
                if pdates_death['ordinal_early'] < pdates_death['ordinal_late']:
                    hdplutils.add_trace_part(self.figure, 
                                pdate_start=max(startpoint,pdates_death['ordinal_early']), 
                                pdate_end=pdates_death['ordinal_late'], 
                                label=text, y=y, color=color, width=1, dash='dot', hovertext=hovertext,
                                xmode=self._xmode, dateformat=self._dateformat, pointinterval=self.pointinterval
                                )
                if alive and (pdates_death['ordinal_late'] > startpoint):   # Right arrow 
                    hdplutils.add_trace_marker(fig, pdate=pdates_death['ordinal_late'], y=y, color=color,
                                symbol='arrow-right',
                                hovertext=hovertext, xmode=self._xmode)
        return True


