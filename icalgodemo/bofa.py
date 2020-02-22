import pandas as pd
import numpy as np
import pickle
import os, time, sys


class DataLoader():

    def __init__(self, filename='EURGBP.csv', source='csv'):

        self.source = source
        self.chunksize = 100000
        self.counter = 0
        self.name = filename
        self.hasdata = True

        if source == 'csv':
            self.dataloader = pd.read_csv(filename, iterator=True)

    def next(self):
        if self.source == 'csv':
            if self.counter % self.chunksize == 0:
                try:
                    self.dfslice = self.dataloader.get_chunk(self.chunksize)
                    data = self.dfslice.iloc[0, :].to_dict()
                    self.counter = 1
                except:
                    data = None
            else:
                try:
                    data = self.dfslice.iloc[self.counter, :].to_dict()
                    self.counter += 1
                except IndexError:
                    data = None
                    self.hasdata = False
        return data


class BOFAStrategy():

    def __init__(self, tickdata='EURGBP.csv', signaldata='signal.csv', debug=False):

        self.pnl = []
        self.holdings = []
        self.period = []
        self.startcash = 100
        self.cash = self.startcash
        self.holding = 0
        self.target = 0
        self.lastbid = 0
        self.lastask = 0

        self.tickreader = DataLoader(filename=tickdata)
        self.signalreader = DataLoader(filename=signaldata)

        self.nexttick = self.tickreader.next()
        self.nextsignal = self.signalreader.next()

    def valuation(self):
        if self.holding >= 0:
            self.portfolio_value = self.holding * self.lastbid + self.cash
            self.pnl.append(self.portfolio_value - self.startcash)
            self.holdings.append(self.holding)
            self.period.append(self.lasttime)
        else:
            self.portfolio_value = self.holding * self.lastask + self.cash
            self.pnl.append(self.portfolio_value - self.startcash)
            self.holdings.append(self.holding)
            self.period.append(self.lasttime)
        return None

    def rebalance(self):
        changes = self.target - self.holding
        if changes >= 0:
            self.cash = self.cash - changes * self.lastask
            self.holding = self.target
        else:
            self.cash = self.cash - changes * self.lastbid
            self.holding = self.target
        return None

    def run(self, debug=False):
        self.before_trades()
        # Compare data and signal time
        while self.tickreader.hasdata or self.signalreader.hasdata:
            if pd.to_datetime(self.nexttick['time'], infer_datetime_format=True) < pd.to_datetime(
                    self.nextsignal['timestamp'], infer_datetime_format=True) or not self.signalreader.hasdata:
                self.lasttime = pd.to_datetime(self.nexttick['time'], infer_datetime_format=True)
                self.lastbid = np.float(self.nexttick['bid'])
                self.lastask = np.float(self.nexttick['ask'])
                self.rebalance()
                self.valuation()
                self.target = self.ondata(self.lastbid, self.lastask)
                if debug:
                    print(
                        'Time {} Bid {} Ask {} Target {} Portfolio {}'.format(self.lasttime, self.lastbid, self.lastask,
                                                                              self.target, self.portfolio_value))
                nexttick = self.tickreader.next()
                if nexttick is not None:
                    self.nexttick = nexttick
            else:
                self.lasttime = pd.to_datetime(self.nextsignal['timestamp'], infer_datetime_format=True)
                self.onsignal(self.nextsignal['type'], self.nextsignal['value'])
                if debug:
                    print('Time {} Type {} Value {}'.format(self.lasttime, self.nextsignal['type'],
                                                            self.nextsignal['value']))
                nextsignal = self.signalreader.next()
                if nextsignal is not None:
                    self.nextsignal = nextsignal

    def download_results(self, filename):
        backtest = pd.DataFrame({'Profit': self.pnl, 'Holding': self.holdings}, index=self.period)
        backtest.to_csv('Backtest_{}.csv'.format(filename))
        return None

        ########  Functions to be supplied by user ###############################################

    def before_trades(self):
        return None

    def ondata(self, bid, ask):
        holding = np.random.random()
        return holding

    def onsignal(self, signaltype, signaldata):
        return None


if __name__ == '__main__':

    try:
        tickdata = sys.argv[1]
        signaldata = sys.argv[2]
    except IndexError:
        print('Need to provide filenames for tick and signal data')

    sample = BOFAStrategy(tickdata=tickdata, signaldata=signaldata)
    sample.run(debug=True)
    sample.download_results('Algosoc2020')
