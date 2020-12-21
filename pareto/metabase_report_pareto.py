from plotly.graph_objs import *
import snowflake as snow
from metabase import get_card_results_pandas


def pareto_chart(days_back: int):
    total_dollars = snow.total_cost_by_warehouse(days_back, 'dataviz_tool_wh')
    percentile = 50.0

    df = get_card_results_pandas(5705, {'days_back': days_back})
    df['dollars'] = df.proportion * total_dollars
    df["cum_percentage"] = df.cum_proportion * 100
    df.cum_percentage = df.cum_percentage.round(2)
    df = df[df.cum_percentage <= percentile]
    n = df.shape[0]

    df.card_name = df.card_name.str.slice(0, 52)

    trace1 = {
        "name": "$ Cost",
        "type": "bar",
        "x": df['card_name'],
        "y": df.dollars,
        "marker": {"color": "rgb(231, 138, 195)"}
    }
    trace2 = {
        "line": {
            "color": "rgb(128,128,128)",
            "width": 1.2
        },
        "name": "% Cumulative",
        "type": "scatter",
        "x": df['card_name'],
        'y': df['cum_percentage'],
        "yaxis": "y2"
    }
    trace3 = {
        "line": {
            "dash": "dash",
            "color": "rgba(128,128,128,.45)",
            "width": 1.5
        },
        "name": "25%",
        "type": "scatter",
        "x": df['card_name'],
        "y": [25 for i in range(0, n)],
        "yaxis": "y2"
    }
    data = Data([trace1, trace2, trace3])
    layout = {
        "title": f"{int(percentile)}% of dataviz_tool_wh went to {n} Metabase reports over the last {days_back} days",
        "width": 1500,
        "xaxis": {"tickangle": -90},
        "yaxis": {
            "title": "$ Cost"  # ,
        },
        "height": 623,
        "legend": {
            "x": 0.83,
            "y": 1.3  # ,
        },
        "margin": {
            "b": 250,
            "l": 60,
            "r": 60,
            "t": 65
        },
        "yaxis2": {
            "side": "right",
            "range": [0, 51],
            "overlaying": "y"
        },
        "showlegend": True,
        "annotations": [
            {
                "x": 1.029,
                "y": 0.75,
                "text": "% Cumulative",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "textangle": 90
            }
        ]
    }
    return Figure(data=data, layout=layout)
