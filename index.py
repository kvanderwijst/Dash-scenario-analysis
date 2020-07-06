import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app
from pages import settings, main
from common import data


app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='common-lastmodified-store')
], className="p-5") 


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/settings':
        return settings.layout
    else:
        return main.layout

if __name__ == '__main__':
    app.run_server(debug=True)