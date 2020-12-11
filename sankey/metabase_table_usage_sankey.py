from _collections import defaultdict
import json
from typing import Dict, List
import plotly
import plotly.graph_objects as go
from snowflake import lookup_table_size
from metabase import get_card_results_pandas


def sankey(report_tables: List[Dict], card_id_to_name: Dict[int, str], days_back: int):
    # load report card data, including table names and count of runs
    card_ids = sorted(list(card_id_to_name.keys()))
    card_names = [card_id_to_name[id] for id in card_ids]

    # greys from https://colorbrewer2.org/#type=sequential&scheme=Greys&n=9
    table_color = '#f7f7f7'
    user_color = '#d9d9d9'
    # from https://colorbrewer2.org/#type=qualitative&scheme=Paired&n=12
    table_link_color = '#a6cee3'
    user_link_color = '#b2df8a'
    card_colors = plotly.colors.qualitative.Dark24
    assert len(card_ids) <= len(card_colors)
    card_ids_to_color = { id: index for index, id in enumerate(card_ids) }

    tables_by_card_id = { card['id']: card['tables'] for card in report_tables if card['id'] in card_ids }

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
    labels = card_tables + card_names + users
    node_colors = [table_color for t in card_tables] + \
             [card_colors[card_ids_to_color[id]] for id in card_ids] + \
             [user_color for u in users]
    card_indices = [len(card_tables)] + [len(card_tables) + i for i in range(1, len(card_ids) + 2)]
    card_ids_by_tables = defaultdict(list)
    for card_id, tables in tables_by_card_id.items():
        for table in tables:
            card_ids_by_tables[table].append(card_id)

    link_colors = []
    sources = []
    targets = []
    values = []
    for table in card_tables:
        for card_id in card_ids_by_tables[table]:
            sources.append(labels.index(table))
            targets.append(labels.index(card_id_to_name[card_id]))
            values.append(table_sizes[table])
            link_colors.append(table_link_color)


    # normalize values so that table sizes and run counts have analogous visual encodings
    def normalize(list):
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
                color = link_colors
            )
        )]
    )

    fig.update_layout(title_text="Metabase Report tables (scaled by data size) and users (scaled by number of hits)",
                      font_size=12,
                      height=700)
    return fig