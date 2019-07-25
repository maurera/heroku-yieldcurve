from app import app
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
from LoadData import loaddata
import pandas as pd
import numpy as np

# Dict version (3M vs OIS curve type)
curvetypes = ['3M','OIS','CMT']
merged = {x:loaddata(x) for x in curvetypes}
datelist = {x:merged[x]['Date'].unique() for x in curvetypes}
sos = {x:min(datelist[x]) for x in curvetypes}
eos = {x:max(datelist[x]) for x in curvetypes}
min_sos = min(sos.values())
max_eos = max(eos.values())
maxrate = {x:max(merged[x]['Shocked']) for x in curvetypes}
X = merged['3M'].loc[merged['3M']["Date"]==sos]

# Single curve version
# merged = loaddata('3M')
# datelist = merged['Date'].unique()
# sos = min(datelist)
# eos = max(datelist) #)[:10]
# maxrate = max(merged['Shocked'])
# X = merged.loc[merged["Date"]==sos]

# Starting data
traces=[go.Scatter(x=X['Term'], y=X['Zero Rate'], name='Baseline')]
traces.append(go.Scatter(x=X['Term'], y=X['Shocked'], name='EBA shock'))
layout=go.Layout(showlegend=True,uirevision='static',
                 xaxis={'title': 'Term (months)','title_text':'Rate (%)'},
                 yaxis={'title': 'Rate (%)', 'title_text':'Term (months)','range':[0,maxrate['3M']]},
                 title_text=str(sos)[:10])
oneday = np.timedelta64(30, 'D')/np.timedelta64(1, 'ns')
figorig = go.Figure(data=traces, layout=layout)

layout_tab1 = [
    html.Div("basis"),
    # dcc.Graph(figure=fig,id='my-graph'),
    dcc.Dropdown(id="curve-type", multi=False, value="3M", style={"width": "25%"},
                        options=[{"label":x,"value":x} for x in curvetypes]),
    dcc.Graph(id='graph-shocks'),
    html.Div(children=[dcc.Slider(id='date-slider',min=min_sos,max=max_eos,step=oneday,value=sos['3M'],
                     updatemode='drag',marks={int(x):str(x)[:10] for x in [min_sos,max_eos]})
                       ], style={"width": "80%","margin":"auto"}) # range(1993,2020,5)
]

layout_tab2 = [
    html.Div("some other stuff"),
    dcc.Graph("some really cool figure stuff")
]

layout_tab3 = [
    html.Div("some other stuff333"),
    dcc.Graph("some really cool 333figure stuff")
]

def closestvaliddate(inp,datelist):
    dist = abs(datelist-np.datetime64(inp,"ns")) # input is date in integer form
    mindist = min(dist) #  divide by np.timedelta64(1, 'D') to get days
    return datelist[dist==mindist][0]


@app.callback(Output('graph-shocks', 'figure'),
    [Input('date-slider', 'value'),Input('curve-type', 'value')]) # , [State('graph-shocks', 'figure')]
def update_figure(inpdate,curve):
    # need to find closest date to
    selecteddate = closestvaliddate(inpdate,datelist[curve])
    X = merged[curve].loc[merged[curve]["Date"]==selecteddate]
    traces = [go.Scatter(x=X['Term'], y=X['Zero Rate'], name='Baseline')]
    traces.append(go.Scatter(x=X['Term'], y=X['Shocked'], name='EBA shock'))
    fig = go.Figure(data=traces, layout=layout)
    fig.layout.update(title_text=str(selecteddate)[:10])
    return fig

#
# Scrap
#

# Different ways to set layout. Either in original layout call or with fig.update
#fig.update_xaxes(title_text='Term (months)')
#fig.update_yaxes(tickvals=list(range(0,8,1)))
#fig.update_yaxes(range=[0,maxrate])
# if fig==None: return figorig