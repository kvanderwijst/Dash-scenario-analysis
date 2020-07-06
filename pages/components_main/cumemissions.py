# Import Dash packages
import dash_core_components as dcc
# import dash_html_components as html
# import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output 

# Import extra packages
import plotly.graph_objects as go
import plotly.express as px

# Import app
from app import app
from common import data


component = dcc.Graph(id='main-cumemissions-graph')

@app.callback(
    Output('main-cumemissions-graph', 'figure'),
    [Input('main-selection-store', 'data')])
def update_graphs(selection_ids):

    selection = data.all_scenarios.iloc[selection_ids]
    selection = selection[selection['year'] == 2100]

    showlegend = True
    legend_margin = 30 if showlegend else 0

    fig = {
        'data': [
            dict(
                x=sub_df['damage_coeff'], y=sub_df['CE'],
                showlegend=False,
                name="{}, {}".format(r, minEmissions), mode='lines',
                line={'color': data.r_colors[r], 'dash': data.line_dash[minEmissions], 'simplify': False}
            )
            for (r, minEmissions), sub_df in selection.groupby(['r', 'minEmissions'])
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



