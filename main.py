# coding: utf-8
import pandas as pd 
import numpy as np
import scipy
import scipy.stats as st
from IPython.display import SVG
import xml.etree.ElementTree as ET
import math
from tqdm import tqdm

def dadata(length, caps):
    base_str = "dadata"
    if caps == 1:
        base_str = base_str.upper()
    return (base_str * math.ceil(length/6))[:length]

def draw_poster(data):
    svg = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", version="1.1",
                     height="400", width="300")
    txt_settings = {
        "text_anchor":"start",
        "font-family":"Helvetica Neue",
    }
    for ix, row in data.iterrows():
        text = ET.SubElement(svg,"text", 
                             x=str(row.x), y=str(row.y),
                             transform="rotate({} {} {})".format(row.rotation, row.x, row.y),
                            **txt_settings)
        text.set('font-size', str(row.font_size))
        weight_map = ['light', 'regular', 'medium', 'bold']
        text.set('font-weight', weight_map[int(row.weight)])
        stretch_map = ['regular','condensed']
        text.set('font-stretch', stretch_map[int(row.condensed)])
        text.text=dadata(int(row.chars), int(row.caps))
    return ET.tostring(svg, encoding='unicode')


def load_training_data(filename='app/data-capture-2-10-904.csv'):
    df = pd.read_csv('app/data-capture-2-10-904.csv')
    df.drop(['NOTES:', 'Unnamed: 11', 'Unnamed: 12', 'alignment'], axis=1, inplace=True)
    df = df.rename(columns={
        "xxz": "seq",
        "x (out of 300)": "x",
        "y (out of 400)": "y",
        "# of characters": "chars",
        "font size": "font_size",
        "# of words": 'words',
        "lines of text": 'lines',
        "caps or lowercase": 'caps'
        })
    df['weight'] = df['font weight'].apply(lambda x: x.split(' ')[-1])
    df['condensed'] = df['font weight'].str.contains('condensed').astype(int)
    df.drop('font weight', axis=1, inplace=True)
    df = df.replace(
        {'weight':{
            'light': 0,
            'regular': 1,
            'medium': 2,
            'bold': 3
        },
        'caps': {
            'C': 1,
            ' C': 1,
            'L': 0
        }
    })
    df['log_font_size'] = np.log(df.font_size)
    df['log_chars'] = np.log(df.chars)
    df.rotation = df.rotation.apply(fix_angle)
    return df

def fix_angle(angle):
    if angle > 180.0:
        return 360.0 - angle 
    elif angle == 0:
        return 0.0
    else:
        return -angle

def generate_multivariate_gaussian(r, means, stdev, n_samples=500):
    # r is the desired covariance matrix.

    # Generate samples from three independent normally distributed random
    # variables (with mean 0 and std. dev. 1).
    x = st.norm.rvs(size=(r.shape[0], n_samples), 
                    loc=np.reshape(means, (2,1)),
                    scale=np.reshape(stdev, (2,1)))
    # We need a matrix `c` for which `c*c^T = r`.  We can use, for example,
    # the Cholesky decomposition
    
    # Compute the Cholesky decomposition.
    c = scipy.linalg.cholesky(r, lower=True)
 
    # Convert the data to correlated random variables. 
    y = np.dot(c, x)
    return y

def draw_from_closest(data, draw_col, draw_val, target_col):
    data.loc[:,'distance'] = (data[draw_col] - draw_val).abs()
    return_val = data.sort_values('distance').head(5).sample(1).iloc[0][target_col]
    return return_val

class PosterGenerator(object):
    poster_width = 300
    poster_height = 400
    xy_params = {}
    chars_params = None
    dist_choice = {
        'x': st.beta,
        'y': st.beta,
        'chars': st.lognorm
    }
    sims = {}
    n_elements = 12
    data = None
    
    def simulate_data(self, data):
        cols = data.columns
        results = generate_multivariate_gaussian(data.cov().values, 
                                                 data.mean().values, 
                                                 data.std().values)

        res = pd.DataFrame(results).T.rename(columns={i:v for i, v in enumerate(cols)})
        return res
        
    def fit(self, data):
        self.data = data
        for val in range(1, self.n_elements+1):
            xdist = self.dist_choice['x']
            ydist = self.dist_choice['y']
            self.xy_params[val] = {
                'x': xdist.fit(data[data.seq==val].x/self.poster_width),
                'y': ydist.fit(data[data.seq==val].y/self.poster_height)
            }
        self.chars_params = self.dist_choice['chars'].fit(data.chars)
        data['log_chars'] = np.log(data.chars)
        data['log_font_size'] = np.log(data.font_size)
#        char_v_font = data[['log_chars','log_font_size']]
#        self.sims[('chars', 'font_size')] = self.simulate_data(char_v_font)
#        self.sims[('y', 'rotation')] = self.simulate_data(data[['y', 'rotation']]) # TODO: make simulation better
            
    def generate(self):
        elements = []
        for i in range(1, self.n_elements+1):
            element = {}
            # using the seq number draw an X and Y
            xy_sample_params = self.xy_params[i]
            x = self.dist_choice['x'](*xy_sample_params['x']).rvs() * self.poster_width
            y = self.dist_choice['y'](*xy_sample_params['y']).rvs() * self.poster_height
            element.update({'x':x, 'y':y})

            # draw a number of chars, from that draw a font size
            chars = math.floor(self.dist_choice['chars'](*self.chars_params).rvs())
#             fs_sim = self.sims[('chars', 'font_size')].apply(np.exp)
            font_size = draw_from_closest(self.data[['chars','font_size']], 
                                          'chars', chars, 'font_size')
            element.update({'chars':chars, 'font_size':font_size})
            
            # from Y, draw a rotation
#            rot_sim = self.sims[('y', 'rotation')]
            rotation = draw_from_closest(self.data[['y','rotation']], 'y', y, 'rotation')
            
            # from font size, draw weight, condensed, and capitalization
            wcc = draw_from_closest(self.data[['font_size','weight', 'condensed', 'caps']], 
                                 'font_size', font_size, ['weight', 'condensed', 'caps'])
            weight, condensed, caps = wcc.values
            element.update({'rotation': rotation, 
                            'weight':weight, 
                            'condensed':condensed, 
                            'caps':caps})
            
            elements.append(element)
        return elements


if __name__ == "__main__":
    df = load_training_data()
    pg = PosterGenerator()
    pg.fit(df)
    for i in tqdm(range(51,100)):
        results = pd.DataFrame(pg.generate())
        with open('generated/generated_{}.svg'.format(i), 'w') as outfile:
            outfile.write(draw_poster(results))
