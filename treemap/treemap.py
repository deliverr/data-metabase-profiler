import plotly.express as px
from metabase import get_card_results_pandas
import snowflake as snow


def treemap(days_back: int):
    df = get_card_results_pandas(6859, {'days_back': days_back})

    df = df[df.period == 'this']
    n = 200
    total_cost = snow.total_cost_by_warehouse(days_back, 'dataviz_tool_wh')
    df["root"] = f"Metabase Top {n} by Author" # in order to have a single root node
    df["cost"] = (df.proportion * total_cost).round(2)
    df["percentage"] = df.proportion * 100
    df["change"] = (df.query_time_pct_change * 100).round(2)
    df.percentage = df.percentage.round(2)
    df["change_in_hours"] = (df.query_time_change / (1000*60*60)).round(2)
    cost_per_ms = total_cost / df['total_time'].iloc[0]
    df["$ change"] = (df.query_time_change * cost_per_ms).round(2)
    topN = df.sort_values('percentage', ascending=False).head(n)
    fig = px.treemap(topN,
                     path=['root', 'first_name', 'card_name'],
                     values='cost',
                     color='$ change',
                     color_continuous_scale="curl", # "balance", # "Fall"
                     color_continuous_midpoint=0,
                     height=700#,
                     #template='%{card_name} %{cost:$.2f}'
                     )

    fig.data[0].texttemplate = "%{label} <br> %{value:$.2f}"

    return fig