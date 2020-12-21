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


def layout(days_back: int, card_ids: List[int]):
    card_id_to_name = {
        4310: 'Rolling_90_Warehouse_Daily_Vol',
        3695: '[cse center] seller sku category opportunities',
        520: 'Log of cdsku'
    }
    if len(card_ids) == 0:
        card_ids = list(card_id_to_name.keys())

    selection_row = dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(
                    id='cards-dropdown',
                    options=[{'label': f"{card['name']} ({card['id']})", 'value': card['id']} for card in report_tables],
                    value=list(card_ids),
                    multi=True
                )
            )
        ]
    )
    sankey_diagram_row = dbc.Row(
        [
            dbc.Col(
                dcc.Graph(id='sankey', figure=sankey(report_tables, card_id_to_name, days_back)), width=12
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


def get_card_by_id(id: int) -> Dict:
    for card in report_tables:
        if card['id'] == id:
            return card
    return None


@application.callback(
    Output('sankey', 'figure'),
    [Input('cards-dropdown', 'value'), Input('days-back', 'children')])
def update_output(value, days_back):
    return sankey(
        report_tables,
        { id: get_card_by_id(id)['name'] for id in value },
        days_back
    )
