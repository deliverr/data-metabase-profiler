"""
Lists Metabase report cards, and the tables the queries reference
"""
import json
import pandas as pd
import sql_metadata
from metabase import get_all_cards, get_card_results_pandas, get_table


def main():
    report_cards = get_all_cards()
    active_cards = get_card_results_pandas(6942, params={ 'days_back': 30 })
    card_ids_to_runs = pd.Series(active_cards.runs, index=active_cards.card_id).to_dict()
    print(f"Retrieved {len(report_cards)} report cards")

    reports = []
    for report_card in report_cards:
        if report_card['dataset_query'] is None:
            print(f"skipping {json.dumps(report_card)}")
            continue
        if report_card['id'] not in card_ids_to_runs:
            print(f"card {report_card['name']} ({report_card['id']}) is not active, skipping")
            continue
        report_tables = {
            "id": report_card['id'],
            "name": report_card['name'],
            "runs": card_ids_to_runs[report_card['id']]
        }
        reports.append(report_tables)
        query_type = report_card['dataset_query']['type']
        if query_type == 'native':
            sql = report_card['dataset_query']['native']['query']
            report_tables["tables"] = sql_metadata.get_query_tables(sql)
        elif query_type == 'query':
            table = get_table(report_card['dataset_query']['query']['source-table'])
            if table is not None:
                report_tables["tables"] = [table['name'].lower()]
            else:
                reports.pop()
        else:
            print(f"Unhandled query type {query_type}")

    with open(f'metabase/report-tables-Snowflake.json', 'w') as outfile:
        json.dump(reports, outfile)


if __name__ == '__main__':
    main()
