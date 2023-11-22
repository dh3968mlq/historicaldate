'''
hdTimeline class definition
'''
import pandas as pd

try:
    import historicaldate.hdtopic as hdtopic
except:
    import historicaldate.historicaldate.hdtopic as hdtopic

# ----------    
class hdTimeLine():
    '''
    Holds a timeline specification, together with line arrangement information
    
    Properties:

    * title (str) : timeline title
    * topics (list of hdTopic): Topics in this timeline
    '''
    def __init__(self, title="", d=None):
        """
        * title (str): timeline title
        * d (dict) (optional): dictionary (as created by *to_dict()*) from which to construct the timeline
        """
        self.topics = []   # List of topics : hdTopic()
        self.title = title
        self._maxid = 0
        self.action_applied = None  # Used to record the last operation. Not updated by methods here, but can be used by clients
        if d:
            self.from_dict(d)
        return
    # ----------    
    def from_dict(self, d):
        """
        Populate an existing hdTimeLine object from a dictionary d (as created by *to_dict()*)
        """
        self.title = d["title"]
        self.topics = []
        self._maxid = 0
        for dtopic in d["topics"]:
            topic = hdtopic.hdTopic()
            topic.from_dict(dtopic)
            self.topics.append(topic)
            self._maxid = max(self._maxid, topic.id)
    # ----------    
    def to_dict(self):
        """
        Convert hdTimeLine object to a dictionary
        """
        d = {"title":self.title,
             "topics":[topic.to_dict() for topic in self.topics]}
        return d
    # ----------    
    def add_topic_df(self, title, df):
        """
        Add a topic passed as Pandas DataFrame *df*
        """
        events = df.to_dict(orient='records')
        self._maxid = self._maxid + 1
        self.topics.append(hdtopic.hdTopic(title, events, id=self._maxid))
    # ----------
    def add_topic_csv(self, title, filename, dataroot="./historicaldate-data/data"):
        """
        Read .csv file and add topic based on its contents.
        """
        df = pd.read_csv(f"{dataroot}/{filename}", na_filter=False)
        self.add_topic_df(title, df)
    # ----------
    def get_date_range(self):
        """
        Calculate earliest and latest date in this timeline, and return them as 
        a duple (earliest, latest) of ordinals
        """
        topic_ranges = [topic.get_date_range() for topic in self.topics]
        mindate = min([topic_range[0] for topic_range in topic_ranges])
        maxdate = max([topic_range[1] for topic_range in topic_ranges])
        return mindate, maxdate
    # ----------
    def get_topic_index(self, id=None):
        "Find the position of a topic in the list, given its id"
        if id:
            for index, topic in enumerate(self.topics):
                if topic.id == id:
                    return index
            return None
        else:
            return None
    # ----------
    def remove_topic(self, id=None):
        "Remove a topic, given its id. Returns True if an item is removed, False otherwise"
        index = self.get_topic_index(id) if id else None

        if index is not None:
            self.topics.pop(index)
            return True
        else:
            return False

