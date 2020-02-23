# Access scripts from 
import sys
sys.path.append('../')
from icalgodemo import BOFAStrategy

import pandas as pd

def func(x):
    EURGBP = pd.read_csv('../icalgodemo/data/EURGBP.csv')
    print(EURGBP.shape)
    return x + 1

def test_answer():
    assert func(3) == 4
