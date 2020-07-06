import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from common import data
from pages.components_main import inputs, NPV, cumemissions, totalnetnegs, emissionpaths, costcomparison

layout = html.Div([
    html.H1('Costs of no net negative emissions'),
    html.H3('Main overview'),
    html.Hr(),

    inputs.component,

    html.Hr(),

    NPV.component,

    dbc.Row([
        dbc.Col([
            html.Strong("Cumulative emissions", id='main-header-cumemissions'),
            dbc.Collapse(cumemissions.component, id='main-content-cumemissions', is_open=True)
        ]),
        dbc.Col([
            html.Strong("Total net negative emissions", id='main-header-totalnetnegs'),
            dbc.Collapse(totalnetnegs.component, id='main-content-totalnetnegs', is_open=True)
        ])
    ]),

    html.Hr(),
    dbc.Row(dbc.Col([
        html.Strong('Emission paths', id='main-header-emissionpaths'), 
        dbc.Collapse(emissionpaths.component, id='main-content-emissionpaths', is_open=True)
    ])),
    html.Br(),
    dbc.Row(dbc.Col([
        html.Strong('Cost comparison paths', id='main-header-costcomparison'),
        dbc.Collapse(costcomparison.component, id='main-content-costcomparison', is_open=True)
    ])),


    html.Hr(),
    dbc.Button("Settings", href="/settings", color="primary", outline=True),

    dcc.Store(id='main-page-store', data={})
])



content_blocks = ['cumemissions', 'totalnetnegs', 'emissionpaths', 'costcomparison']

@app.callback(
    [Output(f"main-content-{name}", 'is_open') for name in content_blocks],
    [Input(f"main-header-{name}", 'n_clicks') for name in content_blocks],
    [State(f"main-content-{name}", 'is_open') for name in content_blocks]
)
def toggle_content(*args):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered == []:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    name = button_id.split('main-header-')[1]
    index = content_blocks.index(name)

    output_values = list(args[len(content_blocks):])
    output_values[index] = not output_values[index]

    return output_values