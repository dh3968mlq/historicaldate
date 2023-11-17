"""
Utilities for figure manipulation in Plotly
"""
import datetime
import plotly.graph_objects as go
from math import ceil

try:
    import historicaldate.hdate as hdate
    import historicaldate.hdateutils as hdateutils
except:
    import historicaldate.historicaldate.hdate as hdate
    import historicaldate.historicaldate.hdateutils as hdateutils

# -----------------------------------------------------------------------------------
def calc_age(ymd_birth, ymd_ref):
    """
    Calculate a person's age from ymd of birth and death

    *ymd_birth*, *ymd_death* must be named tuples, as returned by *hdateutils.to_ymd*
    """
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
    "Calculate age text, including ? to indicate uncertainty, from *plTimeLine().pdates* properties"
    ymd_birth_early = hdateutils.to_ymd(pdates_birth['ordinal_early'])
    ymd_birth_mid = hdateutils.to_ymd(pdates_birth['ordinal_mid'])
    ymd_birth_late = hdateutils.to_ymd(pdates_birth['ordinal_late'])
    ymd_ref_early = hdateutils.to_ymd(pdates_ref['ordinal_early'])
    ymd_ref_mid = hdateutils.to_ymd(pdates_ref['ordinal_mid'])
    ymd_ref_late = hdateutils.to_ymd(pdates_ref['ordinal_late'])

    years_largest = calc_age(ymd_birth_early, ymd_ref_late)
    years_smallest = calc_age(ymd_birth_late, ymd_ref_early)
    uncertain = '?' if years_largest > years_smallest else ""

    years = calc_age(ymd_birth_mid, ymd_ref_mid)
    return f"{years}{uncertain}"
# -----------------------------------------------------------------------------------
def calc_yeartext(pdates, hover_datetype='day'):
    """
    Calculate text to represent a date, including representation of uncertainty,
    from a *plTimeLine().pdates* property
    """
    if hover_datetype not in {'year','month','day'}:
        raise ValueError(f"hover_datetype must be year, month or day. Found:{hover_datetype}")
    
    ymd_early = hdateutils.to_ymd(pdates['ordinal_early'])
    ymd_mid = hdateutils.to_ymd(pdates['ordinal_mid'])
    ymd_late = hdateutils.to_ymd(pdates['ordinal_late'])

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
def _add_trace_marker(fig, pdate=None, label="", y=0.0, 
                   color=None, size=8, symbol='diamond', showlegend=False,
                   hovertext=None, hyperlink=None, xmode="date"):
    """
    Add a single marker to a plot
    """
    pltdate = hdateutils.to_python_date(pdate) if xmode == "date" else hdateutils.to_years(pdate)
    fig.add_trace(go.Scatter(x = [pltdate], y=[y], name=label, legendgroup=label,
                        mode="markers", marker={'color':color, 'size':size,'symbol':symbol}, 
                        hoverinfo='text',
                        hovertext=hovertext if hovertext else label,
                        hoverlabel={'namelength':-1}, showlegend=showlegend))
# ------------------------------------------------------------------------------------------------
def _add_trace_label(fig, pdate=None, label="", y=0.0, hyperlink=None, xmode="date"):
    "Add a label to a plot"
    hlinkedtext = f'<a href="{hyperlink}">{label}</a>' if hyperlink else label
    pltdate = hdateutils.to_python_date(pdate) if xmode == "date" else hdateutils.to_years(pdate)
    fig.add_trace(go.Scatter(x = [pltdate], y=[y+0.04], 
                                name=label, legendgroup=label,
                                mode="text", text=hlinkedtext, 
                                textposition='bottom center',
                                hoverinfo='skip', hoverlabel={'namelength':-1}, showlegend=False))
# ------------------------------------------------------------------------------------------------
def _add_trace_part(figure, pdate_start=None, pdate_end=None, label="", y=0.0, 
                color=None, width=4, dash=None, 
                hovertext=None, hovertext_end=None, 
                xmode="date", dateformat="default", pointinterval=200
                ):
    "Add a line to the figure"
    
    # BC dates are ignored if xmode == "date"
    if xmode == "date" and hdateutils.to_ordinal(pdate_start, dateformat=dateformat) <= 0:
        return

    if hovertext_end is None:
        hovertext_end = hovertext

    if (pdate_start <= pdate_end): 
        if xmode == "date":
            pointinterval = datetime.timedelta(days=pointinterval)
            xs = [hdateutils.to_python_date(pdate_start, dateformat=dateformat) + n * pointinterval for n in 
                range(ceil((hdateutils.to_python_date(pdate_end, dateformat=dateformat) - 
                                    hdateutils.to_python_date(pdate_start, dateformat=dateformat)).total_seconds()/
                                pointinterval.total_seconds()))] + [hdateutils.to_python_date(pdate_end, dateformat=dateformat)]
        else:
            xs = [hdateutils.to_years(hdateutils.to_ordinal(pdate_start, dateformat=dateformat) + n * pointinterval) for n in 
                    range(ceil((hdateutils.to_ordinal(pdate_end, dateformat=dateformat) - 
                                            hdateutils.to_ordinal(pdate_start, dateformat=dateformat))/
                                pointinterval))] + [hdateutils.to_years(pdate_end, dateformat=dateformat)]
        ys = [y for _ in xs]
        hovertexts = label if not hovertext \
                        else hovertext if hovertext == hovertext_end \
                        else [hovertext for _ in range(len(xs) - 1)] + [hovertext_end]
        figure.add_trace(go.Scatter(x = xs, y=ys, name=label, legendgroup=label,
                            mode="lines", line={'color':color,'width':width,'dash':dash}, 
                            hoverinfo='text',
                            hovertext=hovertexts,
                            hoverlabel={'namelength':-1}, showlegend=False))


