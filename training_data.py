import pandas as pd
import numpy as np

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
