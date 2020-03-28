import dash
from datetime import datetime as dt
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import dash_table
from plotly import graph_objs as go
from plotly.graph_objs import *
import numpy as np
import pandas as pd

from utils.visuals import get_spectrogram
from controls import LABELS

import datetime


label_options = [{"label": str(LABELS[label]), "value": str(label)} for label in LABELS]

df = pd.read_csv("data/new_data.csv",
    dtype=object,
)

df1 = pd.read_csv("data/new_data1.csv",
    dtype=object,
)

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

# df = pd.concat([df1,df2,df3], axis=0)
df["Date/Time"] = pd.to_datetime(df["Date/Time"], format="%Y-%m-%d %H:%M")
df.index = df["Date/Time"]
df.drop("Date/Time", 1, inplace=True)
totalList = []
for month in df.groupby(df.index.month):
    dailyList = []
    for day in month[1].groupby(month[1].index.day):
        dailyList.append(day[1])
    totalList.append(dailyList)
totalList = np.array(totalList)
#
node_list = []
node_freq = []
node_dict = {}
for node in df1.groupby(df1['Node']):
    node_dict["Node {}".format(node[0])] = len(node[1])
    node_list.append(node[0])
    node_freq.append(len(node[1]))

print(node_dict)
FILE = "http://localhost:8050/assets/rockstar.mp3"
PATH = "assets/rockstar.mp3"

list_of_locations = {
    "Node 1": {"lat": 33.731210, "lon": 73.036416},
    "Node 2": {"lat": 33.731452, "lon": 73.036368},
    "Node 3": {"lat": 33.731668, "lon": 73.036330},
    "NOde 4": {"lat": 33.732054, "lon": 73.036191},
    "Node 5": {"lat": 33.732324, "lon": 73.036164},
    "Node 6": {"lat": 33.732297, "lon": 73.035801},
    "Node 7": {"lat": 33.732408, "lon": 73.035308},
    "Node 8": {"lat": 33.732493, "lon":73.035042},
    "Node 9": {"lat": 33.732538, "lon": 73.034908},
    "Node 10": {"lat": 33.732578, "lon": 73.034755},
}

def indicator(color, text, id_value):
    return html.Div(
        [
            html.P(id=id_value, className="indicator_value"),
            html.P(text, className="twelve columns indicator_text"),
        ],
        className="four columns indicator pretty_container",
    )






def create_layout(app):
    hist_layout = go.Layout(
        title= "CHECKING HISTOGRAM",
        bargap=0.1,
        bargroupgap=0.1,
        margin=go.layout.Margin(l=50, r=0, t=0, b=25),
        showlegend=True,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        xaxis=dict(
            range=[0, 11],
            showgrid=False,
            fixedrange=False,
        ),
    )

    header_layout = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                    [
                        html.Img(
                            src=app.get_asset_url("forest-nobg.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ], width=3, className="col-sm"),

                    dbc.Col(
                    [

                        html.H3(
                            "Forest Avenger Dashboard",
                        ),

                        html.H5(
                            ["The Forests Initiate"],
                        )

                    ], width=6, className="col-md", style = {"text-align": "center"}),

                    dbc.Col(
                    [
                        # dbc.Button("GitHub Page", href="https://github.com/abdylan/audioAnn_GUI", color="secondary", className="mr-1", size="lg", id="button")
                        html.A(
                            html.Button("GitHub Page", id="learn-more-button"),
                            href="https://github.com/abdylan/audioAnn_GUI",
                        )
                    ], width = 3, className="col-sm")
                ], className = "row justify-content-end")
        ], style={"width": "100%", "margin-left": "3%"},
    )

    tabs_layout = html.Div(
        [
            dbc.Col(
                [
                    # dbc.NavItem(dbc.NavLink("Active", active=True, href="#")),
                    # dbc.NavLink("A link", href="#"),
                    dcc.Link("Audio Analysis", href="/forest-avenger/page1"),
                    dcc.Link("Event History", href="/forest-avenger/page2"),
                ],
                id="tabs",
                className="row tabs",
            ),
        ], style = {"width": "100%", "padding-left": "3%"}
    )

    return html.Div([
        html.Div([
            header_layout,
            html.Br(),
            tabs_layout
        ]),

        html.Div(
            className="row",
            children = [
                # Four Columns
                html.Div(
                    className="six columns div-user-controls",
                    children=[
                        html.Div(
                            className="row",
                            children=[
                                html.H4("Latest Event History"),
                                dash_table.DataTable(
                                    id = 'table',
                                    columns = [{"name": i, "id": i} for i in df1.columns],
                                    data = df1[:12].to_dict('rows'),
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="six columns div-for-charts bg-grey",
                    children=[
                        html.Div(
                            className="text-padding",
                            children=[
                                "Locations of all the Avenger Nodes"
                            ],
                        ),
                        dcc.Graph(id="map-graph"),

                    ],
                ),
            ],
        ),

        html.Div(
            className="row",
            children=[

                html.Div(
                    className="six columns div-for-charts bg-grey",
                    children=[
                        html.Div(
                            className="text-padding",
                            children=[
                                "Events in Every Node"
                            ],
                        ),
                        dcc.Graph(
                            id="histogram1",
                            figure={
                                'data': [
                                    {'x': node_list, 'y': node_freq, 'type': 'bar', 'name': 'Nodes'}
                                ],
                                'layout': hist_layout
                            }

                        ),

                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                html.P(
                                    """Select Node and Date for Alert History"""
                                ),
                                # Dropdown for locations on map
                                dcc.Dropdown(
                                    id="location-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in list_of_locations
                                    ],
                                    placeholder="Select a location",
                                )
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="six columns div-for-charts bg-grey",
                    children=[
                        html.Div(
                            className="text-padding",
                            children=[
                                "Events on the specific Data Time"
                            ],
                        ),
                        dcc.Graph(id="histogram"),
                        html.P(
                            """Select different days using the date picker or by selecting
                            different time frames on the histogram."""
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    min_date_allowed=dt(2014, 4, 1),
                                    max_date_allowed=dt(2014, 9, 30),
                                    initial_visible_month=dt(2014, 4, 1),
                                    date=dt(2014, 4, 1).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[

                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown to select times
                                        dcc.Dropdown(
                                            id="bar-selector",
                                            options=[
                                                {
                                                    "label": str(n) + ":00",
                                                    "value": str(n),
                                                }
                                                for n in range(24)
                                            ],
                                            multi=True,
                                            placeholder="Select certain hours",
                                        )
                                    ],
                                ),
                            ],
                        ),
                        # Html.Div(
                        #
                        # ),
                        # html.P(id="total-rides"),
                        # html.P(id="total-rides-selection"),
                        # html.P(id="date-value"),

                    ],
                ),

            ],
        ),
    ])
