# Import Dash packages
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output 

# Import extra packages
import numpy as np
import pandas as pd
idx = pd.IndexSlice
import plotly.graph_objects as go
import time

# Import app
from app import app
from common import data

# component_fct = lambda name, load_type: dcc.Loading(
#     id='main-NPV-'+name+'-loading',
#     children=dcc.Graph(id='main-NPV-'+name+'-graph'),
#     type=load_type
# )

columns = {
    'utility': ['Utility', 'Utility'], 
    'totalCosts': ['Total costs', 'Total'], 
    'abatementCosts': ['Abatement costs', 'Abat.'], 
    'damageCosts': ['Damages costs', 'Damag.']
}

def title(column):
    return "NPV {} difference".format(columns[column][0].lower())

def component_fct(name, default_column):
    return html.Div([
        html.Strong(title(default_column), id=f"main-NPV-title-{name}"),
        dbc.Tooltip(
            "NPV (no net negs) / NPV (with net negs)",
            target=f"main-NPV-title-{name}",
            placement="bottom"
        ),
        dbc.RadioItems(
            options=[{'label': label[1], 'value': value} for value, label in columns.items()],
            value=default_column, inline=True,
            id=f"main-NPV-input-{name}",
        ),
        html.Hr(className="lessmargin"),
        dbc.RadioItems(
            options=[
                {'label': 'PRTP only', 'value': 'prtp'},
                {'label': 'Ramsey', 'value': 'ramsey_discount'},
                {'label': '5% fixed', 'value': 'fixed5p'}
            ],
            value='prtp', inline=True, id=f'main-NPV-discounting-{name}'
        ),
        # dbc.Checklist(
        #     options=[
        #         {'label': 'As matrix', 'value': 'as_matrix'},
        #         {'label': 'Ramsey discounting', 'value': 'ramsey_discount'}
        #     ],
        #     value=[], inline=True, switch=True,
        #     id=f'main-NPV-options-{name}'
        # ),
        dcc.Graph(id=f'main-NPV-graph-{name}')
    ])

component = dbc.Row([
    dbc.Col(component_fct('1', 'utility'), width=12, md=4),
    dbc.Col(component_fct('2', 'abatementCosts'), width=12, md=4),
    dbc.Col(component_fct('3', 'damageCosts'), width=12, md=4)
])

@app.callback(
    [Output('main-NPV-graph-1', 'figure'),
     Output('main-NPV-graph-2', 'figure'),
     Output('main-NPV-graph-3', 'figure'),
     Output('main-NPV-title-1', 'children'),
     Output('main-NPV-title-2', 'children'),
     Output('main-NPV-title-3', 'children')],
    [Input('main-selection-store', 'data'),
     Input('main-NPV-input-1', 'value'),
     Input('main-NPV-input-2', 'value'),
     Input('main-NPV-input-3', 'value'),
     Input('main-NPV-discounting-1', 'value'),
     Input('main-NPV-discounting-2', 'value'),
     Input('main-NPV-discounting-3', 'value')])
def update_graphs(selection_ids, inp_1, inp_2, inp_3, discounting_1, discounting_2, discounting_3):

    time0 = time.time()

    selection = data.all_scenarios.iloc[selection_ids]
    selection = selection[selection['year'] <= 2100]
    
    NPV_values_1 = create_NPV_difference_df(selection, column=inp_1, options=[discounting_1])
    NPV_values_2 = create_NPV_difference_df(selection, column=inp_2, options=[discounting_2])
    NPV_values_3 = create_NPV_difference_df(selection, column=inp_3, options=[discounting_3])
    fig_1 = create_NPV_difference_fig(NPV_values_1, [discounting_1])
    fig_2 = create_NPV_difference_fig(NPV_values_2, [discounting_2], True)
    fig_3 = create_NPV_difference_fig(NPV_values_3, [discounting_3])

    time1 = time.time()
    print(time1-time0)

    return (
        fig_1, fig_2, fig_3,
        title(inp_1), title(inp_2), title(inp_3)
    )


def create_NPV_difference_fig(NPV_values, options, showlegend=False):
    legend_margin = 70 if showlegend else 0

    if 'as_matrix' in options:
        matrix = NPV_values.set_index(['damage_coeff', 'r'])['change'].unstack()
        traces = [
            dict(
                x=matrix.index.values, y=matrix.columns.values, z=matrix.values.T,
                zmid=1,
                type='heatmap'
            )
        ]
        showlegend=False
        yaxis_layout = {'ticks': matrix.columns.values, 'title': 'PRTP', 'type': 'category'}
    else:
        traces = [
            dict(
                x=sub_df['damage_coeff'], y=sub_df['change'], name=r, mode='lines',
                line={'simplify': False, 'color': data.r_colors[r]}
            )
            for r, sub_df in NPV_values.groupby('r')
        ]
        yaxis_layout = {'title': 'Difference'}

    fig = {
        'data': traces,
        'layout': {
            'showlegend': showlegend,
            'legend': {'y': -0.4, 'x': 0.5, 'orientation': 'h', 'xanchor': 'center'},
            'margin': {'l': 60, 'r': 10, 't': 10, 'b': 60+legend_margin},
            'height': 300+legend_margin,
            'xaxis': {'title': 'Damage coefficient'},
            'yaxis': yaxis_layout,
            #'transition': {'duration': None if 'as_matrix' in options else data.TRANSITION_DURATION}
        }
    }
    return fig



################### CALCULATIONS ###################

def create_NPV_difference_df(selection, column='utility', options=[]):
    """
    Figure of NPV(column; without netnegs) / NPV(column; with netnegs)

    Parameters
    ----------
    selection : dataframe
        Either scenarios or scenarios_inertia
    column : ['utility', 'consumption', 'abatementCosts', ...]
        Column which is discounted

    """
    
    if column == 'totalCosts':
        selection = selection.copy()
        selection['totalCosts'] = selection['abatementCosts'] + selection['damageCosts']

    consumption_per_year = selection.set_index(data.params + ['year'])[column].unstack('year').reset_index('r').set_index('r', append=True, drop=False)
    years = consumption_per_year.columns[1:].values.astype(float)

    PRTPs = consumption_per_year[['r']]
    consumption_per_year.drop(columns='r', inplace=True)
    # if fixed_r is not False:
    #     discount_rates = discount_rates * 0 + fixed_r
    
    # Give every year the same value
    discount_rates = PRTPs.dot([np.ones_like(years)])

    if 'fixed5p' in options:
        discount_rates = discount_rates * 0 + 0.05

    if 'ramsey_discount' in options:
        # For each SSP, add the baseline growth rate for each year
        # TODO: add elasmu from data
        all_elasmu = list(selection['elasmu'].unique())
        elasmu = float(all_elasmu[0])
        if len(all_elasmu) > 1:
            raise Warning('Multiple elasmus not implemented, now using {} instead of {}'.format(elasmu, all_elasmu))
        for SSP in discount_rates.index.get_level_values('SSP').unique():
            discount_rates.loc[idx[SSP,:,:,:,:,:],:] += elasmu * data.carbontaxdamages_economics.growth_rate(years, SSP) 
        

    

    discount_factors = np.exp(-discount_rates * (years-2020))
    discount_factors.columns = consumption_per_year.columns



    NPV_consumption = (discount_factors * consumption_per_year).apply(lambda row: np.trapz(row[~row.isna()], x=row[~row.isna()].index), axis=1).unstack('minEmissions').reset_index()
    NPV_consumption['change'] = NPV_consumption[0] / NPV_consumption[-20]
    
    return NPV_consumption