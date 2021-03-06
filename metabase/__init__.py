"""
Reads queries from Metabase, writes to a migration table and attempts queries through Metabase API
"""
from typing import Dict
import flask
import json
import os
import pandas as pd
from requests_cache import CachedSession
import requests

__DATABASE_ID_SNOWFLAKE__ = os.getenv('METABASE_DATABASE_ID_SNOWFLAKE', '6')
__METABASE_URL__ = os.getenv('METABASE_URL', 'http://localhost')

cached_requests = CachedSession(
    expire_after=60 * 60 * 24, # 24 hours
    allowable_codes=(200, 201, 202, 204),
    allowable_methods=('GET', 'POST'),
    old_data_on_error=True
)


def lower_columns(df: pd.DataFrame):
    df.columns = [col.lower() for col in df.columns]
    return df


def get_metabase_token() -> str:
    if flask.has_request_context() and 'metabase.SESSION' in flask.request.cookies:
        return flask.request.cookies.get('metabase.SESSION')
    elif 'METABASE_TOKEN' in os.environ:
        return os.environ['METABASE_TOKEN']
    raise ValueError("No metabase token found in cookies or environment")


def is_authorized() -> bool:
    res = requests.get(f'{__METABASE_URL__}/api/user/current',
                              headers={'Content-Type': 'application/json',
                                'X-Metabase-Session': get_metabase_token()
                                }
                              )
    return res.status_code == requests.codes.ok


def login_url() -> str:
    return f'{__METABASE_URL__}/auth/login'


def get_card_results_pandas(card_id: int, params: Dict[str, str]) -> pd.DataFrame:
    vars = [{
        "type": "category",
        "target": ["variable", ["template-tag", key]], "value": value}
        for key, value in params.items()
    ]
    result = cached_requests.post(f'{__METABASE_URL__}/api/card/{card_id}/query/json',
                               data={ "parameters": json.dumps(vars) },
                               headers={'Content-Type': 'application/x-www-form-urlencoded',
                                 'X-Metabase-Session': get_metabase_token()
                                 }
                               )
    res_json = result.json()
    if 'json_query' in res_json:
        print(f'SQL compilation errror: {res_json}')
        return pd.DataFrame()
    return lower_columns(pd.DataFrame(res_json))


def get_all_cards(database_id=__DATABASE_ID_SNOWFLAKE__) -> Dict:
    """
    List all report cards for a source database, per
    https://www.metabase.com/docs/latest/api-documentation.html#get-apicard
    BEWARE: May be slow and have a response size in the tens of Megabytes
    :param database_id:
    :return:
    """
    res = requests.get(f'{__METABASE_URL__}/api/card',
                              params={'f': 'database', 'model_id': database_id},
                              headers={'Content-Type': 'application/json',
                                'X-Metabase-Session': get_metabase_token()
                                }
                              )
    return res.json()


def get_table(id: int) -> Dict:
    res = requests.get(f'{__METABASE_URL__}/api/table/{id}',
                              headers={'Content-Type': 'application/json',
                                'X-Metabase-Session': get_metabase_token()
                                }
                              )
    if res.status_code == requests.codes.not_found:
        return None
    return res.json()
