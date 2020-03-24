# Import required libraries
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import os
import numpy as np
import matplotlib.pyplot as plt
import sys
import random
import configparser
from pymongo import MongoClient

from utils.visuals import get_spectrogram
from controls import LABELS

config = configparser.ConfigParser()
config.read('config.ini')

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

label_options = [{"label": str(LABELS[label]), "value": str(label)} for label in LABELS]

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
                html.Div(
                    [
                        dcc.Link("Audio Analysis", href="/"),
                        dcc.Link("Event History", href="/"),
                    ],
                    id="tabs",
                    className="row tabs",
                ),
            ],
        ),

        html.Div(
            id = "lead_grid",
            children = [
                html.Div(
                className="row indicators",
                children=[
                    indicator("#00cc96", "Converted Leads", "left_leads_indicator"),
                    indicator("#119DFF", "Open Leads", "middle_leads_indicator"),
                    indicator("#EF553B", "Conversion Rates", "right_leads_indicator"),
                ],
            ),
            html.Div(
                id="leads_per_state",
                className="chart_div pretty_container",
                children=[
                    html.P("Leads count per state"),
                    dcc.Graph(
                        id="map",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
            ),
            html.Div(
                id="leads_source_container",
                className="six columns chart_div pretty_container",
                children=[
                    html.P("Leads by source"),
                    dcc.Graph(
                        id="lead_source",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
            ),
            html.Div(
                id="converted_leads_container",
                className="six columns chart_div pretty_container",
                children=[
                    html.P("Converted Leads count"),
                    dcc.Graph(
                        id="converted_leads",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
            ),
            ],
        ),
    ],
    className="mainContainer",
)

if __name__ == '__main__':
    app.run_server(debug=False)
