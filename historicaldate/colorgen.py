from plotly import colors as pc

class ColorGen():
    '''
    Cycle through the 10 standard Plotly colors by making calls to get()
    '''
    def __init__(self):
        self.index = -1
        self.colors = pc.DEFAULT_PLOTLY_COLORS
        self.len = len(self.colors)
    def get(self):
        "Return the next color in the standard set"
        self.index += 1
        return self.colors[self.index % self.len]
