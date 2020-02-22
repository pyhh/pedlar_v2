import sys, os
import importlib

TEST_DATA = 'data/EURGBP.csv'
TEST_SIGNALS = 'data/signals.csv'
OUT_PATH = 'results'

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
            output_file = '{}.csv'.format(os.path.join(OUT_PATH, submission.__name__))
            sample.download_results(output_file)
        except:
            output_file = '{}.FAILED'.format(os.path.join(OUT_PATH, sys.argv[1]))
            with open(output_file, 'w') as f:
                pass

