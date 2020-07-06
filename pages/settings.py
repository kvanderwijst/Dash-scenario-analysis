import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from common import data
from pages.components_settings import createcsv, reloadscenarios

back_button = dbc.Button('< Back to content', href='/', color='primary', outline=True)

layout = html.Div([
    html.H1('Costs of no net negative emissions'),
    html.H3('Settings'),
    html.Hr(),
    
    dbc.Row([
        createcsv.component,
        reloadscenarios.component
    ]),

    html.Br(),
    html.Div(id='empty', style={'display': 'none'}),
    html.Hr(),
    back_button
])
