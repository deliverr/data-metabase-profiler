from metabase import get_card_results_pandas
import numpy as np
import os
import pandas as pd

SNOW_COST_PER_CREDIT = float(os.getenv('SNOWFLAKE_COST_PER_CREDIT', default=3.0))


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
