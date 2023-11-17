import utils

class hdTopic():
    '''
    Holds a topic: a list of events and their corresponding ordinals
    '''
    def __init__(self, title="", events=None):
        self.title = title
        self.events = []
        self.ordinals = []
        self.event_display_lines = None
        if events:
            self.events = events
            self.ordinals = [utils.calc_event_ordinals(event) for event in self.events]
    # ---------    
    def from_dict(self, d):
        self.title = d["title"]
        self.events = d["events"]
        self.ordinals = d["ordinals"]
        self.event_display_lines = d["event_display_lines"]
    # ---------    
    def to_dict(self):
        d = {"title": self.title,
             "events":self.events,
             "ordinals":self.ordinals,
             "event_display_lines":self.event_display_lines}
        return d
    # ---------
    def get_date_range(self):
        mindate = min([d["earliest"] for d in self.ordinals])
        maxdate = max([d["latest"] for d in self.ordinals])
        return mindate, maxdate

