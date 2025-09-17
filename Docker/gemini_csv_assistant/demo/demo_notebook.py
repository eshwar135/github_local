# %%
# Demo: Gemini CSV Assistant (client calls backend endpoints)
import requests
from pathlib import Path


BACKEND = 'http://127.0.0.1:8000'


# %%
# 1) Upload sample CSV
csv_path = Path('demo/sample_data/sales_sample.csv')
files = {'file': open(csv_path, 'rb')}
r = requests.post(f'{BACKEND}/upload', files=files)
print('upload ->', r.json())


# %%
# 2) Ask a question
payload = {
'csv_filename': csv_path.name,
'user_query': 'Show top 5 numeric columns by sum'
}
r = requests.post(f'{BACKEND}/ask', json=payload)
resp = r.json()
print('explanation:', resp.get('explanation'))
print('pandas_code:\n', resp.get('pandas_code'))
print('result:', resp.get('result'))


# %%
# 3) Display results nicely in notebook
from pandas import DataFrame
res = resp.get('result')
if res and res.get('type') == 'dataframe':
df = DataFrame(res.get('data'))
display(df)
else:
print(res)