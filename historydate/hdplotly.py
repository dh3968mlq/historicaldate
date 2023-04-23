"""
Plotly timelines for historydate package
"""

import plotly.graph_objects as go

class plTimeLine():
    def __init__(self):
        self.figure = go.Figure()

    def add_hdate_traces(df):
        """
        df must have column 'hdate'
        Optional columns:
            label: String label or identifier
            hdate_end: end of persistent event. hdate is interpreted as the start date.
                If hdate_end is absent, events are treated as single-date events, not persistent events.
            hdate_birth, hdate_death: Birth and death dates
        """
        ...