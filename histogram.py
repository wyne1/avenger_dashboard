# Import required libraries
import copy
import pathlib
import dash
import math
from datetime import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import random
import configparser
from pymongo import MongoClient
import dash_table

from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *

from utils.visuals import get_spectrogram
from controls import LABELS

config = configparser.ConfigParser()
config.read('config.ini')

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)


df1 = pd.read_csv("new_data1.csv",
    dtype=object,
)


node_list = []
node_freq = []
node_dict = {}
for node in df1.groupby(df1['Node']):
    node_dict["Node {}".format(node[0])] = len(node[1])
    node_list.append(node[0])
    node_freq.append(len(node[1]))


# totalList = []

print(node_dict)
FILE = "http://localhost:8050/assets/rockstar.mp3"
PATH = "assets/rockstar.mp3"

def indicator(color, text, id_value):
    return html.Div(
        [
            html.P(id=id_value, className="indicator_value"),
            html.P(text, className="twelve columns indicator_text"),
        ],
        className="four columns indicator pretty_container",
    )

layout = go.Layout(
    title= "CHECKING HISTOGRAM",
    bargap=0.1,
    bargroupgap=0.1,
    # barmode="group",
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
# spec_data = get_spectrogram()

app.layout = html.Div(
    # id = "lead_grid",
    children = [
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("forest.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "SafeCity Monitoring",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Sample SubHeader", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("GitHub Page", id="learn-more-button"),
                            href="https://github.com/abdylan/audioAnn_GUI",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            # style={"margin-bottom": "25px"},
        ),
        html.Br(),
        html.Div(
            [
                dcc.Link("Audio Analysis", href="/"),
                dcc.Link("Event History", href="/"),
            ],
            id="tabs",
            className="row tabs",
        ),

        html.Div(
            className="row",
            children=[
                dash_table.DataTable(
                    id = 'table',
                    columns = [{"name": i, "id": i} for i in df1.columns],
                    data = df1[:10].to_dict('rows'),
                ),
            ],
        ),
    ],
    className="mainContainer",
)


if __name__ == '__main__':
    app.run_server(debug=True)
