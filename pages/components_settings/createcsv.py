# Import Dash packages
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output 

# Import extra packages
import pandas as pd
import numpy as np
import glob
import time
import re
import os

try:
    import json_tricks
    import sys
    sys.path.append('../DamagesAndCarbonPrice') 
    # pylint: disable=import-error
    from carbontaxdamages.defaultparams import Params
    ALLOW_CREATE_CSV = True
except:
    ALLOW_CREATE_CSV = False


# Import app
from app import app
from common import data

component = dbc.Col([
    html.H5('Create CSV from output files'),
    html.Br(),
    html.Div(dbc.Button('Create CSV', color='primary', id='settings-createcsv-button', disabled=(not ALLOW_CREATE_CSV))),
    dbc.Spinner([html.Br(), html.Div(id='settings-createcsv-output'), html.Br()], color='primary')
])

@app.callback(
    Output('settings-createcsv-output', 'children'),
    [Input('settings-createcsv-button', 'n_clicks')]
)
def create_csv_button(value):
    if value and ALLOW_CREATE_CSV:
        time0 = time.time()
        outputs = load_all('experiment_nonegs'+'_*')
        time1 = time.time()
        create_CSV("experiment_nonegs", extra_param_names=['carbonbudget', 'minEmissions', 'maxReductParam', 'damage_coeff', 'T', 'noPositiveEmissionsAfterBudgetYear'])
        time2 = time.time()
        print(time1-time0, time2-time1)
        return "CSV has been updated. {} files found. Took {} seconds.".format(
            len(outputs['experiment_nonegs']),
            np.round(time2-time0, 2)
        )
    return ""



######################## Calculations ###########################

def load_all(file="*"):
    filenames = glob.glob(data.OUTPUT_FOLDER+file+'.json')
    if len(filenames) == 0:
        raise Exception("No files match the given pattern.")

    p_experiment = re.compile('.*(experiment_[a-zA-Z0-9-]+)_')

    outputs = {}
    
    for filename in filenames:
        # First get experiment name
        m = re.match(p_experiment, filename)
        experiment = m.groups()[0] if m else 'default'
        if experiment not in outputs:
            outputs[experiment] = []

        full_filename = u'\\\\?\\' + os.path.abspath(filename)
        with open(full_filename) as fh:
            o = json_tricks.load(fh, preserve_order=False, cls_lookup_map={'Params': Params})
            
        outputs[experiment].append(o)

    return outputs



def create_CSV(name, suffix='', extra_param_names = []):
    outputs = load_all(name+'_*')
    all_df = [pd.DataFrame({
        'name': outp['meta']['shorttitle'],
        'year': outp['meta']['t_values_years'],
        'p': outp['p'],
        'E': outp['E'],
        'baseline': outp['baseline'],
        'Y': outp['Y'],
        'Ygross': outp['Ygross'],
        'consumption': outp['consumption'],
        'utility': outp['utility'],
        'damageFraction': outp['damageFraction'],
        'abatementFraction': (outp['Y'] - (outp['investments'] + outp['consumption'])) / outp['Ygross'],
        'abatementCosts': outp['Y'] - (outp['investments'] + outp['consumption']),
        'CE': outp['cumEmissions'],
        'temp': outp['temp'],
        'perc_reversible': 1,
        'method': 'bellman',
        'SSP': outp['meta']['params'].default_params['SSP'],
        'damage': outp['meta']['params'].default_params['damage'],
        'TCRE': outp['meta']['params'].default_params['TCRE'],
        'cost_level': outp['meta']['params'].default_params['cost_level'],
        'r': outp['meta']['params'].default_params['r'],
        'gamma': outp['meta']['params'].default_params['gamma'],
        'beta': outp['meta']['params'].default_params['beta'],
        'elasmu': outp['meta']['params'].default_params['elasmu'],
        'on_utility': outp['meta']['params'].default_params['maximise_utility'] if 'maximise_utility' in outp['meta']['params'].default_params else np.nan,
        **{name: (outp['meta']['params'].default_params[name] if name in outp['meta']['params'].default_params else '') for name in extra_param_names}
    }) for outp in outputs[name]]

    df = pd.concat(all_df)

    df['p_rel'] = df['p'] / df['gamma']
    
    df.to_csv(data.RESULTS_FOLDER + '{}{}.csv'.format(name,suffix), index=False)
    