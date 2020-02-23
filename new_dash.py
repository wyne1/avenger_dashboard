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
from pydub import AudioSegment
import os
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import wave
import sys

from controls import LABELS
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)


label_options = [
    {"label": str(LABELS[label]), "value": str(label)} for label in LABELS
]

FILE = "http://localhost:8050/assets/rockstar.mp3"
PATH = "assets/rockstar.mp3"
podcast = AudioSegment.from_mp3(PATH)
PODCAST_LENGTH = podcast.duration_seconds
PODCAST_INTERVAL = 500


def seconds_to_MMSS(slider_seconds):
    decimal, minutes = math.modf(slider_seconds / 60.0)
    seconds = str(round(decimal * 60.0))
    if len(seconds) == 1:
        seconds = "0" + seconds
    MMSS = "{0}:{1}".format(round(minutes), seconds)
    return MMSS

def generate_plot(step=1):
    print(PODCAST_INTERVAL * step, PODCAST_INTERVAL * (step + 1))
    # 5 second interval of podcast
    seg = podcast[PODCAST_INTERVAL * step: PODCAST_INTERVAL * (step + 1)]
    samples = seg.get_array_of_samples()
    arr = np.array(samples)
    df = pd.DataFrame(arr)
    df['idx'] = df.index.values
    df.columns = ['y', 'idx']
    fig = px.line(df, x='idx', y='y', render_mode="webgl")
    fig.update_layout(
        height=250,
        margin_r=0,
        margin_l=0,
        margin_t=0,
        yaxis_title="",
        yaxis_fixedrange=True,
    )


    return fig
#
# def generate_plot():
#     spf = wave.open("assets/test-7.wav", "r")
#
#     # Extract Raw Audio from Wav File
#     signal = spf.readframes(-1)
#     signal = np.fromstring(signal, "Int16")
#
#
#     # If Stereo
#     if spf.getnchannels() == 2:
#         print("Just mono files")
#         sys.exit(0)
#
#     plt.figure(1)
#     plt.title("Signal Wave...")
#     plt.plot(signal)

fig = generate_plot()
layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    # mapbox=dict(
    #     accesstoken=mapbox_access_token,
    #     style="light",
    #     center=dict(lon=-78.05, lat=42.54),
    #     zoom=7,
    # ),
)

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

                        dcc.Graph(
                            figure = fig,
                            # id="waveform",
                            # style = {"padding":"30px"}
                        )

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
                        html.H6(
                            "Audio Data Labelling",
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

#
# app.css.append_css({
#     "external_url":"https://codepen.io/chriddyp/pen/bWLwgP.css"
#
# })

if __name__ == '__main__':
    app.run_server(debug=True)
