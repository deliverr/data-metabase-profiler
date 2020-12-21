from typing import Dict, List
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
from application import application
from .metabase_table_usage_sankey import sankey


with open('metabase/report-tables-Snowflake.json', 'r') as infile:
    report_tables = json.load(infile)
    report_options = [{'label': f"{card['name']} ({card['id']})", 'value': card['id']} for card in report_tables]
    reports_by_id = { card['id']: card for card in report_tables}


def layout(days_back: int, card_ids: List[int]):
    selection_row = dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(
                    id='cards-dropdown',
                    options=report_options,
                    value=list(card_ids),
                    multi=True,
                    placeholder='Select report(s)...'
                )
            )
        ]
    )
    sankey_diagram_row = dbc.Row(
        [
            dbc.Col(
                dcc.Graph(id='sankey', figure=sankey(reports_by_id, card_ids, days_back)), width=12
            )
        ]
    )

    content = html.Div(
        [
            selection_row,
            sankey_diagram_row
        ]
    )

    return html.Div([
        content
    ])


@application.callback(
    Output('card-ids', 'children'),
    [Input('cards-dropdown', 'value')])
def update_output(card_ids):
    return card_ids


@application.callback(
    Output('sankey', 'figure'),
    [Input('card-ids', 'children'), Input('days-back', 'children')])
def update_cards(card_ids, days_back):
    return sankey(
        reports_by_id,
        card_ids,
        days_back
    )
