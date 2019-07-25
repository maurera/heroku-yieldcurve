import pandas as pd
import numpy as np
import sys
import datetime as dt
import plotly.offline as py
import plotly.graph_objs as go
import re

# Import yield curve data, apply shocks, and graph

# 1) Load yield curve data
# one file per year (csv)
source = 'C:/Users/andrew.maurer/OneDrive - IHS Markit/Projects/StressTesting/OTCDDData/Historical Data/IR/Yield Curve/USD/USD OIS/Derived Data/'
stub = 'YieldCurve_USD_OIS_DerivedData_'
df = pd.concat([pd.read_csv(source+stub+str(x)+'.csv',parse_dates=True)[['Reference Date','Date','Zero Rate']] for x in range(2007,2019)],
               axis=0,sort=False,ignore_index=True)
df.rename(columns={"Reference Date": "Date", "Date": "Maturity"},inplace=True)
df['Date'] = pd.to_datetime(df['Date'],yearfirst=True)
df['Maturity'] = pd.to_datetime(df['Maturity'],yearfirst=True)
df['Term'] = (round((df['Maturity']-df['Date']).astype('timedelta64[D]')/30)).astype(int)
head = df[df.Date==df.Date[1]]
head = df[df.Date>'2018-10-15']
head.drop_duplicates(subset=['Date','Term'],keep='last',inplace=True)

# 2) Load shock data (single xlsx file)
# data comes in with rows (one per country) and columns (one per term) and values (shock amount). First tab is IR Swap shocks
source = 'C:/Users/andrew.maurer/OneDrive - IHS Markit/Projects/StressTesting/2019-07-16 Fred data/2018 Market Risk Scenarios EBA.xlsx'
sk = pd.read_excel(source,header=1)
sk=sk[sk['Country']=='US']
sk = sk.filter(regex=("^[0-9]+"))
sk = sk.transpose()
sk.columns = ['shock']
sk['Term'] = sk.index
sk['Term'] = sk.index.str.replace('^([0-9]+)[^0-9]+$',r'\1',regex=True).astype(int)
sk['Term'][sk.index.str.match('^[0-9]+Y')]*=12
sk['Term'][sk.index.str.match('^[0-9]+Y\+')]=999
merged = head.merge(sk,how='outer',on='Term',sort=True)
merged['shock'].fillna(method='backfill',inplace=True)
merged.dropna(subset=['Date'],inplace=True)
merged['Shocked']=merged['Zero Rate']+merged['shock']/100

datelist = merged['Date'].unique()
print(merged)
print(sk)


# 3) Combine shocks with yc data
#print(head)
#print(sk)

#sys.exit('asdf')

# 4) Graph
traces=[go.Scatter(x=merged['Term'], y=merged['Zero Rate'], name='Baseline')]
traces.append(go.Scatter(x=merged['Term'], y=merged['Shocked'], name='EBA shock'))
layout=go.Layout(showlegend=True,xaxis={'title': 'Term (months)'},yaxis={'title': 'Rate (%)'})
fig = go.Figure(data=traces,layout=layout)
fig.update_xaxes(title_text='Term (months)')
fig.update_yaxes(title_text='Rate (%)')
#fig.update_yaxes(tickvals=list(range(0,8,1)))
fig.update_yaxes(range=[0,7])
py.plot(fig)

datelist = merged['Date'].unique()
sos = min(datelist)
print(sos)

sys.exit('asdf')


fig = go.Figure(
    data=[go.Scatter(x=head['Term'], y=head['Zero Rate'])],
    layout=go.Layout(
        xaxis=dict(showgrid=True, zeroline=True),
        yaxis=dict(showgrid=True, zeroline=True),
    )
)
#fig.update_yaxes(range=[0, 6])

fig.show()
py.plot(fig)


#fig = go.Figure([data])
#plotly.offline.plot(fig)
#fig.show()
#py.plot(fig)


sys.exit()


# Working plotly example
import plotly.offline as py
import plotly.graph_objs as go
x = np.arange(10)
traces = [go.Scatter(x=x, y=x**2)]
py.plot(data=traces, layout={layout.yaxis.rangemode: 'tozero',layout.xaxis.rangemode: 'tozero'})

sys.exit()


