
# coding: utf-8

# In[136]:


import pandas as pd
import numpy as np
from keras.utils import to_categorical
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Dense, LSTM, TimeDistributed, Concatenate
import keras


# In[137]:


def encode_categoricals(df, col_names):
    for col in col_names:
        onehots = to_categorical(df[col].values)
        onehot_df = pd.DataFrame(onehots, columns=[col + "_" + str(i) for i in range(onehots.shape[1])])
        df = pd.concat([df.drop(col, axis=1), onehot_df], axis=1)
    return df


# In[138]:


def convert_to_padded_seqs(df):
    seqs = []
    subseq = []
    for ix, row in df.iterrows():
        if row['seq'] == 1 and subseq != []:
            seqs.append(subseq)
            subseq = []
        row = row.drop('seq')
        subseq.append(list(row.values))
    sequences = pad_sequences(seqs, padding='post', dtype='float64')
    return sequences


# In[139]:


def fix_angle(angle):
    if angle > 180.0:
        return 360.0 - angle 
    elif angle == 0:
        return 0.0
    else:
        return -angle


# In[140]:


# Convert to a DataFrame and render.
import pandas as pd
df = pd.read_csv('app/data-capture-2-7-940.csv')
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
         'L': 0
     }
})
df = encode_categoricals(df, ['weight'])
continuous_vars = ['seq','x', 'y', 'rotation', 'font_size', 'chars', 'lines']
df.rotation = df.rotation.apply(fix_angle)
df = df[continuous_vars]


# In[142]:


df


# In[141]:


keras_ready[0, 0]


# In[85]:


def scale_df(df):
    new_df = pd.DataFrame()
    new_df['seq'] = df.seq
    new_df['x'] = (df.x - 150.0) / 150.0
    new_df['y'] = (df.y - 200.0) / 200.0
    new_df['rotation'] = df.rotation / 180
    new_df['font_size'] = df.font_size / df.font_size.max()
    new_df['chars'] = df.chars / df.chars.max()
    new_df['lines'] = df.lines / df.lines.max()
    return new_df


# In[107]:


keras_ready = convert_to_padded_seqs(scale_df(df))


# In[115]:


inp = keras.Input((None, 6))
rnn = LSTM(16, activation='tanh', dropout=0.5, return_sequences=True)(inp)
dense1 = TimeDistributed(Dense(3, activation='linear'))(rnn)
dense2 = TimeDistributed(Dense(3, activation='relu'))(rnn)
output = Concatenate()([dense1, dense2])
model = keras.models.Model(input=inp, output=output)
model.compile(loss='mean_squared_error',
              optimizer='adam')


# In[129]:


X = keras_ready[:,:-1,:]
Y = keras_ready[:,1:,:]
h = model.fit(x=X, y=Y, batch_size=1, epochs=10)


# In[130]:


keras_ready[None, [0],[1],:]


# In[131]:


model.predict(keras_ready[None, [0],[0],:])


# In[160]:


from IPython.display import SVG
import xml.etree.ElementTree as ET
import math

def dadata(length):
    return ("dadata" * math.ceil(length/6))[:length]

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
                             #TODO: WEIGHT
                            )
        text.set('font-size', str(row.font_size))
        text.text=dadata(int(row.chars))
    return ET.tostring(svg)


# In[162]:


SVG(draw_poster(df[:12]))


# In[ ]:


df. 

