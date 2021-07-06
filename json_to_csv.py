import pandas as pd

df = pd.read_json (r'./data/output_0.json')
df.to_csv (r'./data/output_0.csv', index = None)