# Import Dash packages
import dash_core_components as dcc
import dash_html_components as html
# import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output 

# Import extra packages
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Import app
from app import app
from common import data

damage_coeffs = data.all_scenarios['damage_coeff'].unique()

component = html.Div([
    dcc.Graph(id='main-emissionpaths-graph'),
    dcc.Slider(
        id='main-emissionpaths-slider',
        min=0, max=len(damage_coeffs)-1,
        step=1,
        marks={
            0: 'DICE',
            1: '',
            2: 'Howard Total',
            3: '',
            4: '',
            5: '',
            6: 'Burke LR'
        },
        value=0,
        updatemode='drag'
    ),
    html.Center('Damage coefficient') 
])

@app.callback(
    Output('main-emissionpaths-graph', 'figure'),
    [Input('main-selection-store', 'data'),
     Input('main-emissionpaths-slider', 'value')])
def update_graphs(selection_ids, damage_coeff_i):
    damage_coeff = damage_coeffs[damage_coeff_i]
    
    selection = data.all_scenarios.iloc[selection_ids]
    selection = selection[selection['damage_coeff'].round(3) == np.round(damage_coeff, 3)]

    fig = {
        'data': [
            dict(
                x=sub_df['year'], y=sub_df['E'],
                line={'color': data.r_colors[r], 'dash': data.line_dash[minEmissions], 'simplify': False},
                name="{}, {}".format(r, minEmissions), mode='lines',
                showlegend=False
            )
            for (r, minEmissions), sub_df in selection.groupby(['r', 'minEmissions'])
        ],
        'layout': {
            'margin': {'l': 50, 'r': 30, 't': 10, 'b': 60},
            'height': 300,
            'yaxis': {'range': [-22, 39], 'title': 'GtCO<sub>2</sub>/year'},
            # 'transition': {'duration': data.TRANSITION_DURATION},
        }
    }
    return fig

