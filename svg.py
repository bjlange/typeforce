import math
import xml.etree.ElementTree as ET
import pandas as pd

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
    for _, row in data.iterrows():
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

def encode_svg(filename):
    tree = ET.parse(filename)
    svg = tree.getroot()
    
    elements = []
    for el in svg:
        element = dict(el.items())
        element['chars'] = len(el.text)
        if el.text == el.text.upper():
            element['caps'] = 1
        else:
            element['caps'] = 0
        elements.append(element)

    data = pd.DataFrame(elements)
    data.drop(['font-family', 'text_anchor'], axis=1, inplace=True)
    data.loc[:,'transform'] = data['transform'].apply(lambda x: x.split(' ')[0].replace('rotate(',''))
    data = data.reset_index()
    data.loc[:, 'index'] = data['index'] + 1
    data.rename(columns={
        'index':'seq',
        'transform':'rotation',
        'font-size': 'font_size',
        'font-stretch': 'condensed',
        'font-weight': 'weight'
    }, inplace=True)
    data.replace(
        {'weight':{
            'light': 0,
            'regular': 1,
            'medium': 2,
            'bold': 3
        },
        'condensed': {
            'condensed': 1,
            'regular': 0
        }},
        inplace=True
    )
        
    
    return data