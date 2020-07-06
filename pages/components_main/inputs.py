# Import Dash packages
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


# Import extra packages
import numpy as np
import time

# Import app
from app import app
from common import data

def create_options(column, only_values=False):
    values = np.sort(data.all_scenarios[column].unique())
    if only_values:
        return values
    return [{'label': value, 'value': value} for value in values]



component = dbc.Row([
    dbc.Col([
        html.P('Cost level'),
        dcc.Dropdown(
            id="main-inputs-cost_level",
            options=create_options('cost_level'),
            value=create_options('cost_level')[1]['value']
        )
    ]),
    dbc.Col([
        html.P('TCRE'),
        dcc.Dropdown(
            id="main-inputs-TCRE",
            options=create_options('TCRE'),
            value=create_options('TCRE')[0]['value']
        )
    ]),
    dbc.Col([
        html.P('Discount rate'),
        dbc.Checklist(
            id='main-inputs-r',
            options=create_options('r'),
            value=create_options('r', True),
            inline=True
        )
    ], width=2.5),
    dbc.Col([
        html.P('Carbon budget'),
        dcc.Dropdown(
            id="main-inputs-carbonbudget", 
            options=create_options('carbonbudget'),
            value=create_options('carbonbudget')[0]['value']
        )
    ]),
    dbc.Col([
        html.P('With inertia'),
        dbc.Checklist(
            id="main-inputs-inertia",
            options=[{"label": "", "value": 1}],
            value=[1],
            switch=True
        )
    ]),
    dbc.Col([
        html.P('% reversible'),
        dcc.Dropdown(
            id="main-inputs-perc_reversible", 
            options=create_options('perc_reversible'),
            value=1
        )
    ]),
    dbc.Col([
        html.P('Method'),
        dbc.RadioItems(
            id="main-inputs-method",
            options=[{"label": "Bellman", "value": 'bellman'}, {'label': 'Pyomo', 'value': 'pyomo'}],
            value='bellman'
        )
    ]),
    dcc.Store(id='main-selection-store')
], className="sticky-top main-inputs-bar")




@app.callback(
    Output('main-selection-store', 'data'),
    [Input('main-inputs-cost_level', 'value'),
     Input('main-inputs-TCRE', 'value'),
     Input('main-inputs-r', 'value'),
     Input('main-inputs-carbonbudget', 'value'),
     Input('main-inputs-inertia', 'value'),
     Input('main-inputs-perc_reversible', 'value'),
     Input('main-inputs-method', 'value')])
def update_store(cost_level, TCRE, r_values, carbonbudget, inertia, perc_reversible, method):

    if cost_level == None or TCRE == None or carbonbudget == None or len(r_values) == 0:
        raise PreventUpdate

    return create_selection_ids(data.all_scenarios, cost_level, TCRE, r_values, carbonbudget, inertia, perc_reversible, method)

def create_selection_ids(all_scenarios, cost_level, TCRE, r_values, carbonbudget, inertia, perc_reversible, method):
    selection_bools = (
        (all_scenarios['cost_level'] == cost_level)
        & (all_scenarios['damage_coeff'] > 0)
        & (all_scenarios['TCRE'] == TCRE)
        & (all_scenarios['carbonbudget'] == carbonbudget)
        & (all_scenarios['r'].isin(r_values))
        & (all_scenarios['withInertia'] == (inertia == [1]))
        & (
            (all_scenarios['perc_reversible'] == perc_reversible)
             | (all_scenarios['minEmissions'] == 0)  # Reversibility doesn't matter here
             | (all_scenarios['damage_coeff'] == 0)) # Reversibility doesn't matter here
        & (all_scenarios['method'] == method)
    )

    selection_ids = list(np.nonzero(selection_bools.values)[0])

    return selection_ids


@app.callback(
    [Output('main-inputs-cost_level', 'options'),
     Output('main-inputs-TCRE', 'options'),
     Output('main-inputs-carbonbudget', 'options'),
     Output('main-inputs-cost_level', 'value'),
     Output('main-inputs-TCRE', 'value'),
     Output('main-inputs-carbonbudget', 'value')],
    [Input('main-page-store', 'data')]
)
def update_options(value):
    print('Creating options')
    return (
        create_options('cost_level'), create_options('TCRE'), create_options('carbonbudget'),
        'p50', '0.00062', 600
    )