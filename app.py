import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
from pydub import AudioSegment
import os
import math

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# file_name = "../rockstar.mp3"
import os

print(os.getcwd())
file_name = "http://localhost:8050/assets/test-7.wav"

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

    # Set custom x-axis labels
#     fig.update_xaxes(
#         ticktext=[seconds_to_MMSS(i + step * 5) for i in range(6)],
#         tickvals=[i * 100000 for i in range(6)],
#         tickmode="array",
#         title="",
#     )

    return fig


FILE = "http://localhost:8050/assets/rockstar.mp3"
PATH = "assets/rockstar.mp3"
podcast = AudioSegment.from_mp3(PATH)
PODCAST_LENGTH = podcast.duration_seconds
PODCAST_INTERVAL = 500

fig = generate_plot()
# app.layout = html.Div([html.Audio(id='audio', src=file_name, controls=True)])


colors = {
    'audio': '#7BEC97',
    'background': '#207D32',
    'text': '#000000'
}

app.layout = html.Div(
    children=[
        html.H4(children="AVENGING FOREST DASHBOARD", style={
            'textAlign': 'center',
            'color': colors['text']}),
        dcc.Markdown(style={
            'textAlign': 'center',
            'color': colors['text']},
            children="Forest Avenger Alerts dashboard tester." 
        ),
    html.Div(id="slider-output-container"),
    html.Br(),
    
    html.Div(
        children = [html.Audio(id="player", src=FILE, controls=True, style={
            "width": "60%"})
    ]),
    dcc.Graph(id="waveform", figure=fig, style={
            "width": "60%"
        })
#     html.Div([html.Audio(id="player", src=FILE, controls=True, autoPlay=False)])
])

if __name__ == '__main__':
    app.run_server(debug=True)