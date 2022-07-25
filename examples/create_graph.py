import requests
import pandas as pd
pd.options.plotting.backend = "plotly"
import plotly.express as px

DB_SERVICE_URL = 'http://127.0.0.1:5001'
response = requests.get(DB_SERVICE_URL + '/query-earnings')

df = pd.DataFrame(response.json().get('response'))
df = df.set_axis(['Name', 'Employee Number', 'Month', 'Day', 'Year', 'Amount', 'ID'], axis=1, inplace=False)
df2 = df.groupby(['Month']).sum()
print(df2['Amount'])

fig = px.line(df2, x=df2.index, y="Amount", title='Earnings')
fig.write_html("templates/home-earnings-graph.html")
