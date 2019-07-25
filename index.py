import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from layouts import layout_tab1, layout_tab2, layout_tab3
from app import app
from app import server

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app.layout = html.Div(
    children=[
        dcc.Tabs(
            id='tabs',
            children=[
                dcc.Tab(label='EBA Shocks', value='tab1'),
                dcc.Tab(label='BOE Shocks', value='tab2'),
                dcc.Tab(label='FRB Shocks', value='tab3')
            ],
            value='tab1'
        ),
        html.Div(id='tab-output')
    ]
)

@app.callback(
    Output('tab-output', 'children'),
    [Input('tabs', 'value')])
def show_content(value):
    if value == 'tab1':
        return layout_tab1
    elif value == 'tab2':
        return layout_tab2
    elif value == 'tab3':
        return layout_tab3
    else:
        return html.Div()

if __name__ == '__main__':
    app.run_server(debug=True)