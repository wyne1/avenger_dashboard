# Import required libraries
import pickle
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

from utils.visuals import get_spectrogram
from pymongo import MongoClient

from controls import LABELS

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

## COSMOS DB Connection + PRINTING INFO
cosmos_uri = "mongodb://test-cosmo-forest:PAmUpODh7NUBRUql5zyzi2EdYyTHWWvjFOIeGbmvUTvMspity4lgpT5L69wmrqgmNvgnVMY1QTxxjUIwnjZjiw==@test-cosmo-forest.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@test-cosmo-forest@"
cosmos_client = MongoClient(cosmos_uri)

print("Mongo Connection Successful. Printing Mongo Details ...")
print(dict((db, [collection for collection in cosmos_client[db].list_collection_names()])
             for db in cosmos_client.list_database_names()))


label_options = [
    {"label": str(LABELS[label]), "value": str(label)} for label in LABELS
]

FILE = "http://localhost:8050/assets/rockstar.mp3"
PATH = "assets/rockstar.mp3"

spec_data = get_spectrogram()

app.layout = html.Div(
    [
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
                                    "Avenging Forests",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Revenge for the Forests", style={"margin-top": "0px"}
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
            [
                html.Div(
                    [
                        html.H3(
                            "Audio Data Analysis",
                            className="audio_label"
                        ),
                        html.H6(
                            "Detected Audio Sound",
                            className="audio_label"
                        ),
                        html.Br(),
                        html.Audio(
                            id="player",
                            src=FILE,
                            controls=True
                        ),
                        html.H6(
                            "Audio Graph",
                        ),
                        html.Img(
                        	id='spectrogram',
                        	src="data:image/png;base64,{}".format(spec_data),
                        	style = {"padding":"30px"})
                        # dcc.Graph(
                        #     figure = fig,
                        #     # id="waveform",
                        #     # style = {"padding":"30px"}
                        # )
                    ],
                    className="eight columns",
                    id="audio_analysis"
                ),

                html.Div(
                    id="vertical_line",
                    className="one columns"
                ),

                html.Div(
                    [
                        html.H3(
                            "Audio Data Labelling",
                            className="audio_label"
                        ),
                        html.H6(
                            "Predicted Labels",
                        ),
                        html.P(
                            "Labels predicted by AI Model",
                        ),
                        dcc.Dropdown(
                            id="client_label2",
                            options=label_options,
                            multi=True,
                            value=list(LABELS.keys()),
                            className="dcc_control",
                        ),
                        html.H6(
                            "Label the Audio",
                        ),
                        html.P(
                            "Choose all labels that you feel are present in the audio"
                        ),
                        dcc.Dropdown(
                            id="client_label",
                            options=label_options,
                            multi=True,
                            # value=list(LABELS.keys()),
                            className="dcc_control",
                        ),
                        html.Span(
                            "Submit",
                            id="submit-sample-button",
                            n_clicks=0,
                            className="button_labels",
                        ),
                        # html.A(
                        #     html.Button("Submit", id="submit-sample-button"),
                        #     href="/",
                        # ),
                        html.Div(children=[],
                            id="button-output"
                        )
                    ],
                    className="five columns",
                    id="audio_label",
                    # style={"padding-top": "0px", "margin-top": "0px"}
                ),
            ],
            id="parent_div",
            className="flex-display"
        ),

    ],
    className="mainContainer",
)

@app.callback(
    Output("button-output", "children"),
    [Input("submit-sample-button", "n_clicks")],
    [
        State("client_label", "value")
    ]
)
def button_submit(n_clicks, human_labels):
    print("Button Clicked!! ", n_clicks)
    print(human_labels)

    ## Submit Labels + Meta to Cosmos DB

    dummy_text = html.P("Submitted Labels!!")
    return dummy_text

#
# app.css.append_css({
#     "external_url":"https://codepen.io/chriddyp/pen/bWLwgP.css"
#
# })

if __name__ == '__main__':
    app.run_server(debug=True)
