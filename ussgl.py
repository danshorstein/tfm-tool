import pandas as pd

columns = ['Desc', 'Comm', 'Ref', 'BDR', 'BCR', 'PDR', 'PCR', 'MDR', 'MCR', 'Debits', 'Credits']

df = pd.read_json('ussgl.json')
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

