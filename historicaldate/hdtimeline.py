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
    A timeline contains a list of topics, and a topic contains a list of events
    '''
    def __init__(self, title="", d=None, jsonstr=None):
        self.topics = []   # List of topics : hdTopic()
        self.title = title
        if d:
            self.from_dict(d)
        return
    # ----------    
    def from_dict(self, d):
        self.title = d["title"]
        self.topics = []
        for dtopic in d["topics"]:
            topic = hdtopic.hdTopic()
            topic.from_dict(dtopic)
            self.topics.append(topic)
    # ----------    
    def to_dict(self):
        d = {"title":self.title,
             "topics":[topic.to_dict() for topic in self.topics]}
        return d
    # ----------    
    def add_topic(self, title, df):
        events = df.to_dict(orient='records')
        self.topics.append(hdtopic.hdTopic(title, events))
    # ----------
    def add_topic_csv(self, title, filename, dataroot="./historicaldate-data/data"):
        df = pd.read_csv(f"{dataroot}/{filename}", na_filter=False)
        self.add_topic(title, df)
    # ----------
    def get_date_range(self):
        topic_ranges = [topic.get_date_range() for topic in self.topics]
        mindate = min([topic_range[0] for topic_range in topic_ranges])
        maxdate = max([topic_range[1] for topic_range in topic_ranges])
        return mindate, maxdate
# -------------------------------------------------------------------------------------------------------    
