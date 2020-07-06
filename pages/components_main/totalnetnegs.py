# Import Dash packages
import dash_core_components as dcc
# import dash_html_components as html
# import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output 

# Import extra packages
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
# import time

# Import app
from app import app
from common import data


component = dcc.Graph(id='main-totalnetnegs-graph')

@app.callback(
    Output('main-totalnetnegs-graph', 'figure'),
    [Input('main-selection-store', 'data')])
def update_graphs(selection_ids):

    selection = data.all_scenarios.iloc[selection_ids]
    selection = selection[selection['year'] <= 2100]
    
    total_net_negs = calculate_total_net_negs(selection)

    showlegend = True
    legend_margin = 30 if showlegend else 0

    fig = {
        'data': [
            dict(
                x=sub_df['damage_coeff'], y=sub_df['total_net_negs'],
                line={'color': data.r_colors[r], 'dash': data.line_dash[minEmissions], 'simplify': False},
                name="{}, {}".format(r, minEmissions), mode='lines',
                showlegend=False
            )
            for (r, minEmissions), sub_df in total_net_negs.groupby(['r', 'minEmissions'])
        ] + [
            dict(
                x=[None], y=[None], mode='lines',
                line={'color': '#000', 'dash': dash},
                showlegend=True,
                name='min: {} GtCO2'.format(minEmissions)
            )
            for minEmissions, dash in data.line_dash.items()
        ],
        'layout': {
            'legend': {'y': -0.4, 'x': 0.5, 'orientation': 'h', 'xanchor': 'center'},
            'margin': {'l': 50, 'r': 10, 't': 10, 'b': 60+legend_margin},
            'height': 300+legend_margin,
            'xaxis': {'title': 'Damage coefficient'},
            'yaxis': {'title': 'GtCO<sub>2</sub>'},
            # 'transition': {'duration': data.TRANSITION_DURATION}
        }
    }
    return fig



def calculate_total_net_negs(selection):
    unique_years = selection['year'].unique()
    # dt = unique_years[1] - unique_years[0]

    net_negative_emissions = selection[['year', 'E'] + data.params].copy()
    net_negative_emissions['E'] = net_negative_emissions['E'].clip(upper=0)

    new_years = np.linspace(unique_years[0], unique_years[-1], 200)
    finer_interpolation = lambda sub_df: np.trapz(np.clip(np.interp(new_years, sub_df['year'], sub_df['E']), None, 0), new_years)

    # Group each scenario and perform linear integration (trapezoid summing)
    # Note that this overestimates the total negative emissions due to the clipping
    total_net_negs = net_negative_emissions.groupby(data.params).apply(finer_interpolation)
    # Transform multi-index Series to dataframe, and rename column to better name
    total_net_negs = total_net_negs.reset_index().rename(columns={0: 'total_net_negs'}) 

    return total_net_negs