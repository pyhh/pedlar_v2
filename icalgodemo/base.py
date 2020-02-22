import csv
import pandas as pd
import numpy as np
import sys, os


class DataLoader:

    def __init__(self, filename='EURGBP.csv', source='csv'):

        self.source = source
        self.counter = 0
        self.name = filename
        self.has_data = True
        self.formats = {
            'bid': lambda x: np.float(x),
            'ask': lambda x: np.float(x),
            'type': lambda x: np.int(x),
            'time': lambda x: pd.to_datetime(x, format='%Y%m%d %H:%M:%S.%f'),
        }

        if source == 'csv':
            self.data = csv.reader(open(filename))
            self.columns = self.data.__next__()

    def next(self):
        try:
            data = dict(zip(self.columns, self.data.__next__()))
            for key, value in data.items():
                if key in self.formats:
                    data[key] = self.formats[key](value)
        except (StopIteration, IndexError):
            data = None
            self.has_data = False
        return data


class BaseStrategy():

    def __init__(self, tick_data='EURGBP.csv', signal_data='signal.csv'):

        self.pnl = []
        self.holdings = []
        self.period = []
        self.start_cash = 10000
        self.cash = self.start_cash
        self.holding = 0
        self.target = 0
        self.last_bid = 0
        self.last_ask = 0
        self.last_time = None
        self.min_holding = -1000
        self.max_holding = 1000

        self.tick_reader = DataLoader(filename=tick_data)
        self.signal_reader = DataLoader(filename=signal_data)

        self.next_tick = self.tick_reader.next()
        self.next_signal = self.signal_reader.next()

    def valuation(self):
        if self.holding >= 0:
            self.portfolio_value = self.holding * self.last_bid + self.cash
            self.pnl.append(self.portfolio_value - self.start_cash)
            self.holdings.append(self.holding)
            self.period.append(self.last_time)
        else:
            self.portfolio_value = self.holding * self.last_ask + self.cash
            self.pnl.append(self.portfolio_value - self.start_cash)
            self.holdings.append(self.holding)
            self.period.append(self.last_time)
        return None

    def rebalance(self):
        changes = self.target - self.holding
        if changes >= 0:
            self.cash = self.cash - changes * self.last_ask
            self.holding = self.target
        else:
            self.cash = self.cash - changes * self.last_bid
            self.holding = self.target
        return None

    def run(self, debug=False):
        self.before_trades()
        # Compare data and signal time
        while self.tick_reader.has_data and self.signal_reader.has_data:
            if self.next_tick['time'] < self.next_signal['time'] or not self.signal_reader.has_data:
                self.last_time = self.next_tick['time']
                self.last_bid = self.next_tick['bid']
                self.last_ask = self.next_tick['ask']
                self.rebalance()
                self.valuation()
                new_target = self.on_tick(self.last_bid, self.last_ask)
                if new_target is not None:
                    self.target = np.clip(new_target, self.min_holding, self.max_holding)
                if debug:
                    print('Time {} | Tick   | Bid {} Ask {} Target {} Portfolio {}'.format(
                        self.last_time, self.last_bid, self.last_ask, self.target, self.portfolio_value))
                next_tick = self.tick_reader.next()
                if next_tick is not None:
                    self.next_tick = next_tick
            else:
                self.last_time = self.next_signal['time']
                new_target = self.on_signal(self.next_signal['type'], self.next_signal['value'])
                if new_target is not None:
                    self.target = np.clip(new_target, self.min_holding, self.max_holding)
                if debug:
                    print('Time {} | Signal | Type {} Value {}'.format(
                        self.last_time, self.next_signal['type'], self.next_signal['value']))
                next_signal = self.signal_reader.next()
                if next_signal is not None:
                    self.next_signal = next_signal

    def download_results(self, file_path=None):
        file_path = 'results.csv' if file_path is None else file_path
        backtest = pd.DataFrame({'Profit': self.pnl, 'Holding': self.holdings}, index=self.period)
        backtest.to_csv(file_path)

        ########  Functions to be supplied by user ########

    def before_trades(self):
        return None

    def on_tick(self, bid, ask):
        holding = self.holding
        return holding

    def on_signal(self, signal_type, signal_value):
        holding = self.holding
        return holding


if __name__ == '__main__':

    try:
        tick_data = sys.argv[1]
        signal_data = sys.argv[2]
    except IndexError:
        print('Need to provide file names for tick and signal data')

    sample = BaseStrategy(tick_data=tick_data, signal_data=signal_data)
    sample.run(debug=True)
    sample.download_results()
