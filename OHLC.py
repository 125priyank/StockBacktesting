import pandas as pd

class OHLC:
    def __init__(self, filename):
        self.df = pd.read_csv(filename)

        # Remove unnessary columns
        self.df.drop('6', axis=1, inplace=True)
        self.df.drop('Unnamed: 0', axis=1, inplace=True)

        self.df.Date = pd.DatetimeIndex(self.df.Date)

        self.findInterval()

    def findInterval(self):
        '''
        '''
        dayRanges = []
        # Store mapping with keys as number of ohlc data in a given day
        # and value as count of number days having that number
        mp = {}
        i = 0
        while i < self.df.shape[0]:
            j = i
            while j < self.df.shape[0] and o.df.Date[i].day == o.df.Date[j].day:
                j+=1
            dayRanges.append((i, j))
            if j-i in mp:
                mp[j-i]+=1
            else:
                print(self.df.Date[i], i)
                mp[j-i]=1
            i = j
        

        print(mp)
