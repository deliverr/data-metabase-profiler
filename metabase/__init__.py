"""
Reads queries from Metabase, writes to a migration table and attempts queries through Metabase API
"""
from typing import Dict
import flask
import os
import pandas as pd
import requests

__DATABASE_ID_SNOWFLAKE__ = '6'
# TODO: get from a dropdown selection
__DAYS_BACK__ = '30'


def get_metabase_token() -> str:
    if flask.has_request_context() and 'metabase.SESSION' in flask.request.cookies:
        return flask.request.cookies.get('metabase.SESSION')
    elif 'METABASE_TOKEN' in os.environ:
        return os.environ['METABASE_TOKEN']
    raise ValueError("No metabase token found in cookies or environment")


def get_card_results_pandas(card_id: int, params: Dict[str, str]) -> pd.DataFrame:
    vars = [{
        "type": "category",
        "target": ["variable", ["template-tag", key]], "value": value}
        for key, value in params.items()
    ]
    res = requests.post(f'https://metabase.deliverr.com/api/card/{card_id}/query',
                        json={ "ignore_cache": False, "parameters": vars },
                        headers={'Content-Type': 'application/json',
                                 'X-Metabase-Session': get_metabase_token()
                                 }
                        )
    results = res.json()
    return pd.DataFrame(
        data=results["data"]["rows"],
        columns=[col["name"].lower() for col in results["data"]["cols"]]
    )


def get_all_cards(database_id=__DATABASE_ID_SNOWFLAKE__) -> Dict:
    """
    List all report cards for a source database, per
    https://www.metabase.com/docs/latest/api-documentation.html#get-apicard
    BEWARE: May be slow and have a response size in the tens of Megabytes
    :param database_id:
    :return:
    """
    res = requests.get(f'https://metabase.deliverr.com/api/card',
                       params={'f': 'database', 'model_id': database_id},
                       headers={'Content-Type': 'application/json',
                                'X-Metabase-Session': get_metabase_token()
                                }
                       )
    return res.json()


def get_table(id: int) -> Dict:
    res = requests.get(f'https://metabase.deliverr.com/api/table/{id}',
                       headers={'Content-Type': 'application/json',
                                'X-Metabase-Session': get_metabase_token()
                                }
                       )
    if res.status_code == requests.codes.not_found:
        return None
    return res.json()