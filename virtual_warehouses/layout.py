import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from donut import donut_chart
from stacked_bar import stacked_bar_chart
from pareto import pareto_chart


def layout(days_back: int):
    content_first_row = dbc.Row(
        [
            dbc.Col(
                dcc.Graph(id='donut', figure=donut_chart(days_back)), width=5
            ),
            dbc.Col(
                html.Span(), width=1
            ),
            dbc.Col(
                dcc.Graph(id='stacked-bar', figure=stacked_bar_chart(days_back)), width=5
            )
        ]
    )
    content_second_row = dbc.Row(
        [
            dbc.Col(
                dcc.Graph(id='pareto', figure=pareto_chart(days_back)), width=12
            )
        ]
    )

    content = html.Div(
        [
            content_first_row,
            content_second_row
        ]
    )

    return html.Div([
        content
    ])
