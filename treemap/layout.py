import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from .treemap import treemap


def layout(days_back: int):
    content_first_row = dbc.Row(
        [
            dbc.Col(
                dcc.Graph(id='treemap', figure=treemap(days_back)), width=12
            )
        ]
    )

    content = html.Div(
        [
            content_first_row
        ]
    )

    return html.Div([
        content
    ])
