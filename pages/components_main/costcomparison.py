# Import Dash packages
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# Import extra packages
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Import app
from app import app
from common import data
from pages.components_main import emissionpaths

component = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Checklist(
                options=[
                    {'label': 'Discounted', 'value': 'discounted'},
                    {'label': 'Ramsey discounting', 'value': 'ramsey_discount'},
                    {'label': 'Cumulative', 'value': 'cumulative'},
                    {'label': 'Until 2200', 'value': 'longrun'},
                    {'label': 'Fixed axes', 'value': 'fixedaxes'}
                ],
                value=['fixedaxes'],
                inline=True, switch=True,
                id='main-costcomparison-options', className='m-2'
            )
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='main-costcomparison-graph')
        ]),
        dbc.Col([
            dcc.Graph(id='main-costcomparison-graph2')
        ]),
        dbc.Col([
            dcc.Graph(id='main-costcomparison-graph3')
        ])
    ])
])

@app.callback(
    [Output('main-costcomparison-graph', 'figure'),
     Output('main-costcomparison-graph2', 'figure'),
     Output('main-costcomparison-graph3', 'figure')],
    [Input('main-selection-store', 'data'),
     Input('main-emissionpaths-slider', 'value'),
     Input('main-costcomparison-options', 'value')])
def update_graphs(selection_ids, damage_coeff_i, options):
    damage_coeff = emissionpaths.damage_coeffs[damage_coeff_i]

    selection = data.all_scenarios.iloc[selection_ids]
    selection = selection[
        (selection['damage_coeff'].round(3) == np.round(damage_coeff, 3))
        & (selection['year'] <= (2200 if 'longrun' in options else 2100))
    ]

    
    return (
        create_fig(selection, 'abatementCosts', options),
        create_fig(selection, 'damageCosts', options),
        create_fig(selection, 'utility', options, 0.03)
    )

def create_fig(selection, column, options, yrange_factor=1):
    
    if 'fixedaxes' in options:
        yrange = [-5.82 * yrange_factor, (1396 if 'cumulative' in options else 55.18) * yrange_factor]
    else:
        yrange = None

    fig = {
        'data': [
            dict(
                x=sub_df['year'], y=calc_costs(sub_df, column, r, options),
                line={'color': data.r_colors[r], 'dash': data.line_dash[minEmissions], 'simplify': False},
                name="{}, {}".format(r, minEmissions), mode='lines',
                showlegend=False
            )
            for (r, minEmissions), sub_df in selection.groupby(['r', 'minEmissions'])
        ],
        'layout': {
            'margin': {'l': 50, 'r': 30, 't': 10, 'b': 60},
            'height': 300,
            'yaxis': {
                'range': yrange,
                'title': column
            },
            'transition': {'duration': data.TRANSITION_DURATION},
        }
    }
    return fig


def calc_costs(sub_df, column, r, options):

    values = sub_df[column].values
    years = sub_df['year'].values

    if 'discounted' in options:
        if 'ramsey_discount' in options:
            SSP = sub_df['SSP'].iloc[0]
            elasmu = float(sub_df['elasmu'].iloc[0])
            discount_rate = float(r) + elasmu * data.carbontaxdamages_economics.growth_rate(years, SSP) 
        else:
            discount_rate = float(r)
        output = np.exp(-discount_rate * (years - 2020)) * values
    else:
        output = values

    if 'trapz' in options:
        return np.trapz(output, x=years)

    if 'cumulative' in options:
        output = np.cumsum(output) * (years[1] - years[0])
    return output