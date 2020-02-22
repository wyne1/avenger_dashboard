import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
from pydub import AudioSegment
import os
import math


app = dash.Dash(__name__)

FILE = "http://localhost:8050/assets/rockstar.mp3"
server = app.server

app.layout = html.Div(
    [
        html.Div(
            className = "row header",
            children = [
                html.Button(id="menu", children=dcc.Markdown("&#8801")),
                html.Span(
                    className="app-title",
                    children=[
                        dcc.Markdown("**Avenging Forests**"),
                        html.Span(
                            id="subtitle",
                            children=dcc.Markdown("&nbsp : Revenge for the Forests"),
                            style={"font-size": "1.8rem", "margin-top": "5px"},
                        ),
                    ],
                ),
                html.A(
                    id="learn_more",
                    children=html.Button("Learn More"),
                    href="https://plot.ly/dash/",
                ),
            ],

        ),


        html.Div(
            id="tabs",
            className="row tabs",
            children=[
                dcc.Link("Alerts", href="/"),
                dcc.Link("History", href="/"),
            ],
        ),


        html.Div(
            id="audio",
            className = "row audio",
            children=[
                html.Audio(id="player", src=FILE, controls=True)
            ],
        ),


        #SECOND DIV ENDS HERE



    ]
)

app.css.append_css({
    "external_url":"https://codepen.io/chriddyp/pen/bWLwgP.css"

})

if __name__ == '__main__':
    app.run_server(debug=True)
