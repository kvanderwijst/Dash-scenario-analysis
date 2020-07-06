import pandas as pd
import plotly.express as px

TRANSITION_DURATION = 200
RESULTS_FOLDER = '../DamagesAndCarbonPrice/'
# RESULTS_FOLDER = './results/'
OUTPUT_FOLDER = RESULTS_FOLDER + 'output/'

DATA_FILENAME = 'experiment_nonegs_combined.csv'
# DATA_FILENAME = 'experiment_nonegs.csv'

COLORS_PBL = ['#00AEEF', '#808D1D', '#B6036C', '#FAAD1E', '#3F1464', '#7CCFF2', '#F198C1', '#42B649', '#EE2A23', '#004019', '#F47321', '#511607', '#BA8912', '#78CBBF', '#FFF229', '#0071BB']

# import sys
# sys.path.append(RESULTS_FOLDER) 
# pylint: disable=import-error
from . import carbontaxdamages_economics

###### Load common data

COEFF_DICE = 0.00267
COEFF_HOWARD = 0.010038
COEFF_BURKE = 0.026142

all_scenarios = None

params = ['SSP', 'damage_coeff', 'TCRE', 'cost_level', 'r', 'minEmissions']
line_dash = {0: 'dot', -20: 'solid'}
r_colors = dict(zip([0.001, 0.015, 0.03], COLORS_PBL))

def load_data():
    global all_scenarios
    print('Start importing data')
    all_scenarios = pd.read_csv(RESULTS_FOLDER+DATA_FILENAME, dtype={
        'TCRE': str, 'elasmu': str, 'beta': str, 'gamma': str, 'damage': str, 'noPositiveEmissionsAfterBudgetYear': str}
    )
    all_scenarios['withInertia'] = all_scenarios['maxReductParam'] < 50

    all_scenarios['damageCosts'] = all_scenarios['damageFraction'] * all_scenarios['Ygross']

    max_dmg_coeff = 0.026143 # Burke LR damage coefficient
    all_scenarios = all_scenarios[
        (all_scenarios['damage_coeff'] <= max_dmg_coeff)
        & (all_scenarios['damage_coeff'] > 0)
    ]
    all_scenarios = all_scenarios.sort_values(['cost_level', 'TCRE', 'r', 'carbonbudget', 'damage_coeff', 'year'])

    print('Done.')  

    return all_scenarios

load_data()
