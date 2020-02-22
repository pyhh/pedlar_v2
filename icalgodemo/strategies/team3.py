import sys
from pedlar_v2.icalgodemo.base import BaseStrategy


class Strategy(BaseStrategy):

    def on_tick(self, bid, ask):
        """
        This function is called after each tick.
        To change the holding to N units long, return N
        To change the holding to N units short, return -N
        :param bid: the current bid price
        :param ask: the current ask price
        :return: a float in the range [-1,1] representing the desired holding
        """
        raise Exception('Whoopsie')


if __name__ == '__main__':

    try:
        tick_data = sys.argv[1]
        signal_data = sys.argv[2]
    except IndexError:
        print('Need to provide filenames for tick and signal data')

    sample = Strategy(tick_data=tick_data, signal_data=signal_data)
    sample.run(debug=True)
    sample.download_results()