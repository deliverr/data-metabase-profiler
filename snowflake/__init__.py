from metabase import get_card_results_pandas
import numpy as np
import os
import pandas as pd

SNOW_COST_PER_CREDIT = float(os.getenv('SNOWFLAKE_COST_PER_CREDIT', default=3.0))

# source Snowflake query
# SELECT table_schema,
#        table_name,
#        active_bytes / (1024 * 1024 * 1024) AS storage_usage_GB
# FROM   "INFORMATION_SCHEMA".table_storage_metrics
# where table_catalog in ('PROD')
# order by storage_usage_GB desc;
table_sizes_raw = pd.read_csv('snowflake/table_sizes.csv')


def lower_columns(df: pd.DataFrame):
    df.columns = [col.lower() for col in df.columns]
    return df


def cost_from_credits(df: pd.DataFrame, credits_col: str, cost_col: str):
    df[cost_col] = (df[credits_col] * SNOW_COST_PER_CREDIT).round()
    return df


def total_cost_by_warehouse(days_back: int, warehouse='dataviz_tool_wh'):
    credits_df = get_card_results_pandas(
        6898,
        {
            'days_back': days_back,
            'warehouse_name': warehouse
        }
    )

    total_credits = credits_df['total_credits_used'].iloc[0]
    return total_credits * SNOW_COST_PER_CREDIT


def lookup_table_size(table: str) -> np.float64:
    name = table
    if '.' in table:
        schema, name = table.split('.')
        # print(f"Looking up {table} as {schema}.{name}")
        matches = (table_sizes_raw['TABLE_SCHEMA'] == schema.upper()) & \
                  (table_sizes_raw['TABLE_NAME'] == name.upper())
        if matches.sum() > 0:
            return table_sizes_raw[matches]['STORAGE_USAGE_GB'].tolist()[0]
    else:
        # print(f"Looking up {name}")
        matches = table_sizes_raw['TABLE_NAME'] == name.upper()
        # parsing of table names from SQL by sql_metadata can include column names
        if matches.sum() > 0:
            return table_sizes_raw[matches]['STORAGE_USAGE_GB'].tolist()[0]

    if name.upper().startswith('VIEW_'):
        return lookup_table_size(name[5:])

    return 1 # todo: throw error, caller lookup size for view or remove a column mistaken as table
