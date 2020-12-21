import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from application import application, server
from dash.dependencies import Input, Output
import re
from metabase import is_authorized, login_url
import virtual_warehouses
import treemap
import sankey


def parse_days_back_hash(hash: str) -> int:
    if hash is not None and hash.startswith('#days-'):
        days = re.search(r'#days-([0-9]{1,2})', hash)
        return int(days.group(1))
    else:
        return 30


def generate_navbar(days_back: int):
    return dbc.NavbarSimple(
        children=[
            dbc.DropdownMenu(
                id='days-back-dropdown',
                children=[dbc.DropdownMenuItem(f"last {days} days", href=f"#days-{days}", active=days == days_back)
                          for days in [14, 30]],
                nav=False,
                in_navbar=True,
                label=f"last {days_back} days",
                color="info",
                style={ 'padding-right': '35px' }
            ),
            dbc.NavItem(dbc.NavLink("Virtual Warehouses", href=f"/profiler/virtual-warehouses#days-{days_back}")),
            dbc.NavItem(dbc.NavLink("Report TreeMap", href=f"/profiler/metabase-reports#days-{days_back}")),
            dbc.NavItem(dbc.NavLink("User Hits & Table Sizes", href=f"/profiler/users-and-tables#days-{days_back}")),
        ],
        brand="Metabase Profiler",
        brand_href=f"/profiler/virtual-warehouses#days-{days_back}",
        color="primary",
        dark=True,
        fluid=False
    )


def serve_layout():
    if not is_authorized():
        return dcc.Link("You will first need to login to Metabase, then return to /profiler", href=login_url())

    return html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Location(id='url', refresh=False),
                html.Div(id='days-back', hidden=True),
                html.Div(id='navbar', children=[
                    generate_navbar(30)
                ]),
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id='page-content', children=[]),
                html.Div(id='card-ids', hidden=True, children=[]),
            ], width=12)
        ])
    ])


application.layout = serve_layout


@application.callback(Output('page-content', 'children'),
                      Output('days-back', 'children'),
                      Output('navbar', 'children'),
                      [Input('url', 'pathname'), Input('url', 'hash'), Input('card-ids', 'children')])
def display_page(pathname, hash, card_ids):
    if hash is not None:
        days_back = parse_days_back_hash(hash)
    if pathname == '/profiler/virtual-warehouses':
        layout = virtual_warehouses.layout(days_back)
    elif pathname == '/profiler/metabase-reports':
        layout = treemap.layout(days_back)
    elif pathname == '/profiler/users-and-tables':
        layout = sankey.layout(days_back, card_ids)
    else:
        layout = virtual_warehouses.layout(days_back)
    return layout, days_back, generate_navbar(days_back)


if __name__ == '__main__':
    application.run_server(debug=True, host='0.0.0.0')