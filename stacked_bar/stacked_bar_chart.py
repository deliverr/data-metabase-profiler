import plotly.express as px
import snowflake as snow
from metabase import get_card_results_pandas
import plotly


def stacked_bar_chart(days_back: int):
    df = get_card_results_pandas(3218, {'days_back': days_back})
    df['warehouse_name'] = df.warehouse_name.str.lower()
    warehouse_names = df \
        .warehouse_name \
        .drop_duplicates() \
        .sort_values() \
        .tolist()

    df = snow.cost_from_credits(df, 'warehouse_credits_used', 'warehouse_cost')
    df['$ cost'] = df.warehouse_cost
    df['date'] = df.usage_date
    df['virtual warehouse'] = df.warehouse_name
    return px.bar(
        df,
        "date",
        y="$ cost",
        color="virtual warehouse",
        title=f"Daily Cost per Virtual Warehouse",
        category_orders={"virtual warehouse": warehouse_names},
        color_discrete_sequence=plotly.colors.qualitative.Set2 # Dark2 # D3
    )


