import sys
import numpy as np
from pedlar_v2.icalgodemo.base import BaseStrategy


class Strategy(BaseStrategy):

    def on_tick(self, bid, ask):
        """
        This function is called after each tick.
        To change the holding to N units, return N
        :param bid: the current bid price
        :param ask: the current ask price
        :return: a float in the range [-1000, 1000] representing the desired holding
        """
        holding = self.holding
        return holding

    def on_signal(self, signal_type, signal_value):
        """
        This function is called each time a new signal arrives.
        To change the holding to N units, return N
        :param signal_type: an integer representing the type of signal received
        :param signal_value: a string representing the value of the signal.
        :return: a float in the range [-1000, 1000] representing the desired holding
        """
        holding = np.random.randn()
        return holding

    def before_trades(self):
        """
        This function is called before a new signal or tick arrives.
        It can be used to create features (e.g. time since last tick/signal).
        """


if __name__ == '__main__':

    try:
        tick_data = sys.argv[1]
        signal_data = sys.argv[2]
    except IndexError:
        print('Need to provide filenames for tick and signal data')

    sample = Strategy(tick_data=tick_data, signal_data=signal_data)
    sample.run(debug=True)
    sample.download_results()