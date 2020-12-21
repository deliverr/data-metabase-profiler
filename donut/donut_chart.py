import plotly.graph_objects as go
import plotly
import snowflake as snow
from metabase import get_card_results_pandas


def donut_chart(days_back: int):
    df = get_card_results_pandas(3221, params = { 'days_back': days_back })
    df['warehouse_name'] = df.warehouse_name.str.lower()
    df = df.sort_values(by='warehouse_name')
    snow.cost_from_credits(df, 'total_credits_used', 'total_cost')
    df['total_cost'] = df.total_cost.round(2)
    # Use `hole` to create a donut-like pie chart
    pie = go.Pie(
        labels=df.warehouse_name,
        values=df.total_cost,
        hole=.3,
        sort=False,
        marker={"colors": plotly.colors.qualitative.Set2},
        #texttemplate="%{label}: %{value:$,s} <br>(%{percent})",
        texttemplate="%{label} <br>%{value:$,s}",
        textposition="inside"
    )
    fig = go.Figure(data=[
       pie
    ])
    fig.update_layout(
       title_text=f"Snowflake Cost by Virtual Warehouse, last {days_back} days",
       # Add annotations in the center of the donut pies.
       annotations=[dict(text="${:.1f}K".format(df.total_cost.sum() / 1000),
                         x=0.5, y=0.5, font_size=14, showarrow=False)])
    return fig
