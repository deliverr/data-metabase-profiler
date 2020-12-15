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
            dbc.NavItem(dbc.NavLink("Virtual Warehouses", href=f"/virtual-warehouses#days-{days_back}")),
            dbc.NavItem(dbc.NavLink("Metabase Reports", href=f"/metabase-reports#days-{days_back}")),
            dbc.NavItem(dbc.NavLink("Users & Tables", href=f"/users-and-tables#days-{days_back}")),
            dbc.DropdownMenu(
                id='days-back-dropdown',
                children=[dbc.DropdownMenuItem(f"{days} days back", href=f"#days-{days}", active=days == days_back)
                          for days in [14, 30]],
                nav=False,
                in_navbar=True,
                label=f"{days_back} days back",
                color="info"
            )
        ],
        brand="Metabase Profiler",
        brand_href=f"/virtual-warehouses#days-{days_back}",
        color="primary",
        dark=True,
        fluid=True
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
                html.Div(id='page-content', children=[])
            ], width=12)
        ])
    ])


application.layout = serve_layout


@application.callback(Output('page-content', 'children'),
                      Output('days-back', 'children'),
                      Output('navbar', 'children'),
                      [Input('url', 'pathname'), Input('url', 'hash')])
def display_page(pathname, hash):
    if hash is not None:
        days_back = parse_days_back_hash(hash)
    if pathname == '/virtual-warehouses':
        layout = virtual_warehouses.layout(days_back)
    elif pathname == '/metabase-reports':
        layout = treemap.layout(days_back)
    elif pathname == '/users-and-tables':
        layout = sankey.layout(days_back)
    else:
        layout = virtual_warehouses.layout(days_back)
    return layout, days_back, generate_navbar(days_back)


if __name__ == '__main__':
    application.run_server(debug=True, host='0.0.0.0')