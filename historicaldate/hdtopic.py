try:
    import historicaldate.hdtimelineutils as hdtimelineutils
except:
    import historicaldate.historicaldate.hdtimelineutils as hdtimelineutils

class hdTopic():
    '''
    Holds a topic: a list of events and their corresponding ordinals

    Properties:

    * title (str): title of the topic
    * events (list of dict): events in this topic. Dictionary keys are allowed column names in a .csv file as specified in the README
    * ordinals (list of dicts): dictionaries of ordinals corresponding to the dates of events in this topic
    * event_display_lines (list of int): (possible future deprectation): lines on which to display the events
    '''
    def __init__(self, title="", events=None):
        """
        * title (str) : topic title
        * events (list of dict): events with which to populate the topic
        """
        self.title = title
        self.events = []
        self.ordinals = []
        self.event_display_lines = None
        if events:
            self.events = events
            self.ordinals = [hdtimelineutils.calc_event_ordinals(event) for event in self.events]
    # ---------    
    def from_dict(self, d):
        """
        Populate existing hdTopic object from a dictionary d as created by *to_dict()*
        """
        self.title = d["title"]
        self.events = d["events"]
        self.ordinals = d["ordinals"]
        self.event_display_lines = d["event_display_lines"]
    # ---------    
    def to_dict(self):
        """
        Convert hdTopic to a dictionary
        """
        d = {"title": self.title,
             "events":self.events,
             "ordinals":self.ordinals,
             "event_display_lines":self.event_display_lines}
        return d
    # ---------
    def get_date_range(self):
        """
        Calculate earliest and latest date in this topic, and return them as 
        a duple (earliest, latest) of ordinals
        """
        mindate = min([d["earliest"] for d in self.ordinals])
        maxdate = max([d["latest"] for d in self.ordinals])
        return mindate, maxdate

