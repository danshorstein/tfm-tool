import pandas as pd
import os

columns = ['Desc', 'Comm', 'Ref', 'BDR', 'BCR', 'PDR', 'PCR', 'MDR', 'MCR', 'Debits', 'Credits']

directory = base_folder = os.path.abspath(os.path.dirname(__file__))
ussgl_loc = os.path.join(directory, 'ussgl.json')

df = pd.read_json(ussgl_loc)

df = df[columns]

def tc_lookup(drs=None, crs=None):
    sgls = df.copy()
    if drs:
        for dr in drs:
            sgls = sgls.where(df.Debits.str.contains(dr)).dropna()
    if crs:
        for cr in crs:
            sgls = sgls.where(df.Credits.str.contains(cr)).dropna()
    return sgls

