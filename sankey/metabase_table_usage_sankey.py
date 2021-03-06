from collections import defaultdict, ChainMap
import json
import numpy as np
from typing import Dict, List
import plotly
import plotly.graph_objects as go
import sql_metadata
from metabase import get_card_results_pandas


def lookup_table_size(table: str) -> np.float64:
    table_sizes_raw = get_card_results_pandas(7211, {})
    name = table
    if '.' in table:
        schema, name = table.split('.')
        matches = (table_sizes_raw['table_schema'] == schema.upper()) & \
                  (table_sizes_raw['table_name'] == name.upper())
        if matches.sum() > 0:
            return table_sizes_raw[matches]['storage_usage_gb'].tolist()[0]
    else:
        matches = table_sizes_raw['table_name'] == name.upper()
        # parsing of table names from SQL by sql_metadata can include column names
        if matches.sum() > 0:
            return table_sizes_raw[matches]['storage_usage_gb'].tolist()[0]

    if name.upper().startswith('VIEW_'):
        return lookup_table_size(name[5:])

    view_ddl_df = get_card_results_pandas(7212, { 'view': name })
    if not view_ddl_df.empty and 'ddl' in view_ddl_df.columns:
        tables = sql_metadata.get_query_tables(view_ddl_df['ddl'].iloc[0])
        return sum([lookup_table_size(t) for t in tables])
    return 0.001


def sankey(reports_by_id: Dict[int, Dict], card_ids: List[int], days_back: int):
    # load report card data, including table names and count of runs
    selected_cards = [reports_by_id[id] for id in card_ids]
    card_id_to_name = { card['id']: card['name'] for card in selected_cards }

    # greys from https://colorbrewer2.org/#type=sequential&scheme=Greys&n=9
    table_color = '#f7f7f7'
    user_color = '#d9d9d9'
    # from https://colorbrewer2.org/#type=qualitative&scheme=Paired&n=12
    table_link_color = '#a6cee3'
    user_link_color = '#b2df8a'
    card_colors = plotly.colors.qualitative.Dark24
    assert len(card_ids) <= len(card_colors)
    card_ids_to_color = { id: index for index, id in enumerate(card_ids) }

    tables_by_card_id = { card['id']: card['tables'] for card in selected_cards }

    report_runs = get_card_results_pandas(6937, { 'days_back': days_back })
    card_runs = report_runs[report_runs.card_id.isin(card_ids)]

    # format links with tables on left, report cards in middle and users to the right
    flatten = lambda t: [item for sublist in t for item in sublist]
    card_tables = list(set(flatten(tables_by_card_id.values())))
    users_by_card_id = { card_id: card_runs[card_runs.card_id == card_id].first_name.tolist() for card_id in card_runs.card_id }
    users = list(set(flatten(users_by_card_id.values())))

    table_sizes = defaultdict(float)
    for table in card_tables:
        table_sizes[table] = lookup_table_size(table)

    # prep labels, source, target and value network fields for Sankey diagram
    labels = card_tables + list(card_id_to_name.values()) + users
    node_colors = [table_color for t in card_tables] + \
             [card_colors[card_ids_to_color[id]] for id in card_ids] + \
             [user_color for u in users]
    card_ids_by_tables = defaultdict(list)
    for card_id, tables in tables_by_card_id.items():
        for table in tables:
            card_ids_by_tables[table].append(card_id)

    link_colors = []
    sources = []
    targets = []
    values = []
    customdata = list()
    for table in card_tables:
        for card_id in card_ids_by_tables[table]:
            sources.append(labels.index(table))
            targets.append(labels.index(card_id_to_name[card_id]))
            values.append(table_sizes[table])
            customdata.append(f'({round(table_sizes[table], 2)} GB)')
            link_colors.append(table_link_color)

    # normalize values so that table sizes and run counts have analogous visual encodings
    def normalize(list):
        if len(list) == 0:
            return list
        max_value = max(list)
        return [v / max_value for v in list]

    values = normalize(values)

    for card_id, users in users_by_card_id.items():
        card_color = card_ids_to_color[card_id] + 1
        for user in users:
            sources.append(labels.index(card_id_to_name[card_id]))
            link_colors.append(user_link_color)

    user_values = []
    for id in card_ids:
        if id in users_by_card_id:
            for user in users_by_card_id[id]:
                targets.append(labels.index(user))
                user_values.append(card_runs[(card_runs.first_name == user) & (card_runs.card_id == id)].runs.tolist()[0])
        else:
            print(f"No users for for card_id {id}, {json.dumps(users_by_card_id)}")
    customdata += [f'({v} runs)' for v in user_values]
    values += normalize(user_values)

    # draw the diagram
    fig = go.Figure(
        data=[go.Sankey(
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = labels,
                color = node_colors
            ),
            link = dict(
                source = sources,
                target = targets,
                value = values,
                customdata = customdata,
                color = link_colors,
                hovertemplate='%{target.label} reads %{source.label} %{customdata}<br />'
            )
        )]
    )

    fig.update_layout(title_text=f"Report User hits and Source Table sizes, last {days_back} days",
                      font_size=12,
                      height=700)
    return fig