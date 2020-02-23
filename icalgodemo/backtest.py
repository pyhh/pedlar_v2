import sys, os
import importlib
import matplotlib.pyplot as plt

TEST_DATA = 'data/EURGBP.csv'
TEST_SIGNALS = 'data/signals.csv'
OUT_PATH = 'results'


def plot_sample(sample):
    fig, (ax, ax2) = plt.subplots(2, 1)
    ax.plot(sample.pnl, color='blue', label='pnl')
    ax2.plot(sample.holdings, color='red', label='holding', linestyle='--')
    ax2.set_xlabel('ticks')
    ax.set_ylabel('Pnl')
    ax2.set_ylabel('Holding')
    plt.legend()
    plt.tight_layout()
    plt.savefig('{}.png'.format(output_name))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        for filename in os.listdir('strategies'):
            if filename not in ('__init__.py', '__pycache__'):
                os.popen('python backtest.py {}'.format(filename))
    else:
        try:
            script_name = sys.argv[1].split('.')[0]
            module_path = '.icalgodemo.strategies.{}'.format(script_name)
            submission = importlib.import_module(module_path, package='pedlar_v2')
            sample = submission.Strategy(tick_data=TEST_DATA, signal_data=TEST_SIGNALS)
            sample.run()
            output_name = '{}/{}'.format(OUT_PATH, submission.__name__, sample.pnl[-1])
            sample.download_results('{}_{}.csv'.format(output_name, sample.pnl[-1]))
            plot_sample(sample)
        except:
            output_name = '{}.FAILED'.format(os.path.join(OUT_PATH, sys.argv[1]))
            with open(output_name, 'w') as f:
                pass

