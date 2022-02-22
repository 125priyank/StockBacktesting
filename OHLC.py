import pandas as pd

class OHLC:
    def __init__(self, filename):
        self.df = pd.read_csv(filename)
        