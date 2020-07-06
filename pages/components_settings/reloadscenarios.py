# Import Dash packages
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output 

# Import extra packages
import numpy as np
import time

# Import app
from app import app
from common import data

component = dbc.Col([
    html.H5('Reload scenarios'),
    html.Br(),
    html.Div(dbc.Button('Reload scenarios', color='primary', id='settings-reloadscenario-button')),
    dbc.Spinner([html.Br(), html.Div(id='settings-reloadscenario-output'), html.Br()], color='primary')
])

@app.callback(
    [Output('settings-reloadscenario-output', 'children'),
     Output('common-lastmodified-store', 'data')],
    [Input('settings-reloadscenario-button', 'n_clicks')]
)
def reload_scenarios(value):
    if value:
        data.load_data()
        output_message = "Scenarios have been reloaded. Currently {} rows available ({} scenarios)".format(
            len(data.all_scenarios),
            len(data.all_scenarios.groupby(data.params+['withInertia', 'carbonbudget']))
        )
    else:
        output_message = ""
    return output_message, time.time()