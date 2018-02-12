# coding: utf-8
import pandas as pd 
import numpy as np
import scipy
import scipy.stats as st
import math
from tqdm import tqdm

from training_data import load_training_data
from svg import dadata, draw_poster
from model import PosterGenerator

def initial_gen():
    df = load_training_data()
    pg = PosterGenerator()
    pg.fit(df)
    for i in tqdm(range(101,151)):
        results = pd.DataFrame(pg.generate())
        with open('generated/generated_{}.svg'.format(i), 'w') as outfile:
            outfile.write(draw_poster(results))

if __name__ == "__main__":
    initial_gen()