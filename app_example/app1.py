import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input

data = pd.read_csv("avocado1_.csv")
data["Date"] = pd.to_datetime(data['CreateDate']).dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
data["Date"] = pd.to_datetime(data['Date'])
data["Datenew"]  =  pd.to_datetime(data['CreateDate']).dt.strftime('%Y-%m-%d')
data["Datenew"] = pd.to_datetime(data['Datenew'])
data.sort_values("Date", inplace=True)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Sample Analytics: Understand Your Data!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                #html.P(children="🥑", className="header-emoji"),
                html.H1(
                    children="Sample Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze some data"
                    " between 2017 and 2021",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Platform", className="menu-title"),
                        dcc.Dropdown(
                            id="region-filter",
                            options=[
                                {"label": DeviceType, "value": DeviceType}
                                for DeviceType in np.sort(data.DeviceType.unique())
                            ],
                            value="Albany",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="BrowserVersion", className="menu-title"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=[
                                {"label": BrowserMajorVersion, "value": BrowserMajorVersion}
                                for BrowserMajorVersion in sorted( list( data.BrowserMajorVersion.unique() ))
                            ],
                            value="organic",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range", className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.Date.min().date(),
                            max_date_allowed=data.Date.max().date(),
                            start_date=data.Date.min().date(),
                            end_date=data.Date.max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="volume-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    [Output("price-chart", "figure"), Output("volume-chart", "figure")],
    [
        Input("region-filter", "value"),
        Input("type-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(region, avocado_type, start_date, end_date):
    mask = (
        (data.DeviceType == region)
        & (data.BrowserMajorVersion == avocado_type)
        & (data.Date >= start_date)
        & (data.Date <= end_date)
    )

    filtered_data = data.loc[mask, :]
    price_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Id"].count(),
                "type": "lines",
                "hovertemplate": "%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "User count",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data["Datenew"].values,
                "y": filtered_data.groupby('Datenew').agg(
                    # Get sum of the duration column for each group
                    total_duration=('ScreenPixelsWidth', sum),
                )['total_duration'],
                "type": "bars",
            },
        ],
        "layout": {
            "title": {"text": "ScreenOutByRuleId Count", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return price_chart_figure, volume_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)
