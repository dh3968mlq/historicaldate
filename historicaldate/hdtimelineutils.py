try:
    import historicaldate.hdate as hdate
except:
    import historicaldate.historicaldate.hdate as hdate

def calc_date_ordinals(hd, dprefix="", dateformat=None, missingasongoing=False):
    """
    Calculate ordinals for a single date, return as a dictionary with keys
    <dprefix>_early, <dprefix>_mid, <dprefix>_late, <dprefix>_ongoing

    * *hd* (str): A string representing a date in a format recognised by HDate()
    * *dateformat*, *missingasongoing*: as for HDate()

    Other code assumes that any entry in d of type int is an ordinal date
    """
    pd = hdate.HDate(hd, missingasongoing=missingasongoing, dateformat=dateformat).pdates
    if pd:
        d = {f"{dprefix}_early":pd["ordinal_early"],
            f"{dprefix}_mid":pd["ordinal_mid"],
            f"{dprefix}_late":pd["ordinal_late"]}
        d[f"{dprefix}_ongoing"] = (pd['slmid'] == 'o')
    else:
        d = {}
    return d
# ------------------------------------------------------------------------------------------------------------------
def calc_event_ordinals(event, dateformat=None):
    """
    Calculate ordinals for all the dates in an event, return as a dictionary with keys:

    start_early, start_mid, start_late, start_ongoing,
    end_early, end_mid, end_late, end_ongoing,
    birth_early, birth_mid, birth_late, birth_ongoing,
    death_early, death_mid, death_late, death_ongoing,
    earliest, latest, label

    All dictionary values are (int) ordinals, except for ..._ongoing, which are bool
    """
    d = {}
    if (hd := event.get("hdate", None)) is not None: 
        d.update(calc_date_ordinals(hd, "start", dateformat=dateformat))
    if (hd := event.get("hdate_end", None)) is not None: 
        d.update(calc_date_ordinals(hd, "end", dateformat=dateformat))
    if (hd := event.get("hdate_birth", None)) is not None: 
        d.update(calc_date_ordinals(hd, "birth", dateformat=dateformat))
    if (hd := event.get("hdate_death", None)) is not None: 
        d.update(calc_date_ordinals(hd, "death", dateformat=dateformat, 
                        missingasongoing=(d.get("birth_mid", None) is not None)))

    d["earliest"] = min({val for val in d.values() if type(val)==int})
    d["latest"] = max({val for val in d.values() if type(val)==int})

    # -- Calculate the label date
    if d.get("start_mid", None) is not None:
        if d.get("end_mid", None) is not None:
            labeldate = d['start_mid'] + int((d['end_mid'] - d['start_mid'])/2.0)
        else:
            labeldate = d['start_mid']
    elif d.get("birth_mid", None) is not None:
        if d.get("death_mid", None) is not None:
            labeldate = d['birth_mid'] + int((d['death_mid'] - d['birth_mid'])/2.0)
        else:
            labeldate = d['birth_mid']
    d["label"] = labeldate
    return d