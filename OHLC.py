from collections import OrderedDict

import pandas as pd
import numpy as np

class OHLC:
    def __init__(self, filename):
        # Never input df data which is daily, interval should be in minutes, hours
        self.df = pd.read_csv(filename)

        # Remove unnessary columns
        self.df.drop('6', axis=1, inplace=True)
        self.df.drop('Unnamed: 0', axis=1, inplace=True)

        # Convert string dates to pd.Datetime
        self.df.Date = pd.DatetimeIndex(self.df.Date)

        # interval is in minues
        self.interval = None
        self.days = None
        # This is the number of data points in each day
        self.eachDayRows = None

        # Remove wrong data rows from df
        self.cleanDf()
        self.findInterval()

        # Assert no extra wrong rows remain now after cleanup
        assert self.eachDayRows*self.days == self.df.shape[0]

        self.df.set_index('Date', inplace=True) 
        
        # Remove timezone from timestamp
        self.df.index = [i.replace(tzinfo=None) for i in self.df.index]

    def toInterval(self, minutes):
        # Resamples df to the minutes input provided
        OHLCV_AGG = OrderedDict((
            ('Open', 'first'),
            ('High', 'max'),
            ('Low', 'min'),
            ('Close', 'last'),
            ('Volume', 'sum'),
        ))
        freq_minutes = pd.Series({
            "1T": 1,
            "5T": 5,
            "10T": 10,
            "15T": 15,
            "30T": 30,
            "1H": 60,
            "2H": 60*2,
            "4H": 60*4,
            "8H": 60*8,
            "1D": 60*24,
            "1W": 60*24*7,
            "1M": np.inf,
        })

        freq = freq_minutes.where(freq_minutes >= minutes).first_valid_index()
        return self.df.resample(freq, label='left').agg(OHLCV_AGG).dropna()

    def findInterval(self):
        mp = dict()
        i = 0
        dayCnt = 0
        while i < self.df.shape[0]:
            j = i+1
            dayCnt += 1
            while j < self.df.shape[0] and self.df.Date[i].day == self.df.Date[j].day:
                interval = (self.df.Date[j] - self.df.Date[j-1]).total_seconds()
                if interval in mp:
                    mp[interval]+=1
                else:
                    mp[interval]=1
                j+=1
            i = j

        # Assert only one type of interval should exist
        assert(len(mp)) == 1

        # Dividing the interval by 60 to convert seconds to minutes
        self.interval = list(mp.keys())[0]/60
        self.days = dayCnt

    def cleanDf(self):
        def allIntervals():
            # Return a map with 
            # keys -> number of intervals in a day
            # values -> number of days with this interval
            mp = dict()
            i = 0
            while i < self.df.shape[0]:
                j = i
                while j < self.df.shape[0] and self.df.Date[i].day == self.df.Date[j].day:
                    j+=1
                if j-i in mp:
                    mp[j-i].append((i, j))
                else:
                    mp[j-i]=[(i, j)]
                i = j
            return mp
        
        mp = allIntervals()

        # Drop data which is not a most occurring number of interval in a day
        maxlen = 0
        for i in mp.values():
            maxlen = max(maxlen, len(i))
        
        # Store to be deleted indices
        rmIndx = []
        for i in mp.values():
            if len(i) < maxlen:
                for pair in i:
                    rmIndx.extend(np.arange(pair[0], pair[1]))
        
        self.df.drop(rmIndx, axis=0, inplace=True)
        self.df.index = np.arange(0, self.df.shape[0])

        # After cleanup only one type of interval should remain
        mp = allIntervals()
        assert len(mp) == 1
        self.eachDayRows = list(mp)[0]
