import numpy as np
import scipy.stats as st
import scipy
import pandas as pd
import math

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