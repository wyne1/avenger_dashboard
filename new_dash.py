# Import required libraries
from pprint import pprint
import traceback
import time
import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
import os
import numpy as np
import random
import configparser
from pymongo import MongoClient

from utils.mongo_utils import get_doc_count
from utils.visuals import get_spectrogram
from controls import LABELS
from utils.sidebar import sidebar
import datetime as dt
from utils.helpers import append_alertDB_row

config = configparser.ConfigParser()
config.read('config.ini')

app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/brPBPO.css'],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
server = app.server

label_options = [{"label": str(LABELS[label]), "value": str(label)} for label in LABELS]

FILE = "http://localhost:8050/assets/rockstar.mp3"
PATH = "assets/rockstar.mp3"

spec_data = get_spectrogram()

header_layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
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
                ], width=3, className="col-sm"),

                dbc.Col(
                [

                    html.H3(
                        "SafeCity Monitoring",
                    ),

                    html.H5(
                        ["Sample SubHeader"],
                    )

                ], width=6, className="col-md", style = {"text-align": "center"}),

                dbc.Col(
                [
                    html.A(
                        html.Button("GitHub Page", id="learn-more-button"),
                        href="https://github.com/abdylan/audioAnn_GUI",
                    )
                ], width = 3, className="col-sm")
            ], className = "row justify-content-end")
    ], style={"width": "100%"},
)

tabs_layout = html.Div(
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
)

audio_analysis_layout = html.Div(
    [
        dbc.Col([
            html.H3(
                "Audio Data Analysis",
                className="display-4"
            ),
            html.H6(
                "Detected Audio Sound",
                className="display-6"
            ),
            html.Br(),
            html.Audio(
                id="wav-player",
                src=FILE,
                controls=True
            ),
            html.H6(
                "Audio Graph",
            ),
            html.Img(
                id='spectrogram',
                src="data:image/png;base64,{}".format(spec_data),
                )
        ])
    ] , className = "audio_analysis",
)

audio_labelling_layout = html.Div(
    [
        dbc.Col([
            html.H3(
                "Audio Data Labelling",
                className="display-4"
            ),
            html.H6(
                "Predicted Labels",
            ),
            html.P(
                "Labels predicted by AI Model",
            ),
            dcc.Dropdown(
                id="ai-preds",
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
                id="human-labels",
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
        ])
    ],
    className="audio_label_col",
    # style={"padding-top": "0px", "margin-top": "0px"}
)


alert_toast = dbc.Toast(
            "Please check out from Sidebar",
            id="alert-popup",
            header="ALERT !!",
            is_open=True,
            dismissable=True,
            icon="danger",
            duration=10000,
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "top": 20, "right": 10, "width": 550},
        )




app.layout = html.Div(
    [
        dcc.Interval(id="interval-updating-alert", interval=5000, n_intervals=0),
        dcc.Location(id="url"),

        dbc.Col([sidebar, alert_toast,], width = 2),
        dbc.Col(
        [
            dbc.Row([header_layout]),
            dbc.Row([
                dbc.Col([
                    audio_analysis_layout
                ]),
                dbc.Col([
                    audio_labelling_layout
                ]),

            ], id = "audio_row"),
        ], width = 12)
    ], className = "main_div",
)

def find_alert_press(current_q, find_uri):
    target_idx, target_item = -1, None
    final_q = []

    for i, item in enumerate(current_q):
        if find_uri in item["props"].values():
            target_idx = i
            item["props"]["active"] = True
            target_item = item
            final_q.append(item)
        else:
            item["props"]["active"] = False
            final_q.append(item)

    return target_idx, final_q

@app.callback(
    [Output("current_queue", "children"), Output("ai-preds", "value")],
    [Input("url", "pathname")],
    [State("current_queue", "children")])
def alert_item_button(url_path, current_q):
    """
    1) Change LINK Active Status
    2) Update Alert Details (WAV, Spec, ai-preds)

    """
    print("ALERT Item PRESSED: ", url_path)

    target_idx, final_q = find_alert_press(current_q, url_path)

    if target_idx == -1:
        print("Target URL not FOUND!")
        return [current_q, ["cricket", "birds"]]
    else:
        return [final_q, ["footstep", "speech"]]


#########  INTERVAL: Updating UI according to new sample  ############
def append_alert_queue(alert_queue, timestamp, date):
    length_alert_queue = len(alert_queue["props"]["children"])
    new_queue_alert = {'props': {'children': '{}'.format(timestamp),
            'id': 'alert-{}-link'.format(timestamp), 'href': '/{}'.format(timestamp)
            }, 'type': 'NavLink', 'namespace': 'dash_bootstrap_components/_components'}
    alert_queue["props"]["children"].append(new_queue_alert)
    print("[QUEUE] APPENED New ALert to Queue")
    return alert_queue

@app.callback(
    [Output("alert-popup", "is_open"), Output("alert-queue", "children")],
    [Input("interval-updating-alert", "n_intervals")],
    [
        State("current_queue", "children"),
        State("alert-queue", "children")
    ]
)
def interval_alert(n_intervals, current_queue, alert_queue):
    """
    Tasks involced:
    1. Ping Azure For New Predictions/Alerts
    2. RETURN
        i)  Alert Pop-Up
        ii) Navigation Bar Queue - APPEND ONLY
            If new alert, then we APPEND item to Sidebar Queue
            and reeturn the ENTIRE Queue
    """
    if n_intervals is None:
        raise PreventUpdate

    global FILE
    global pred_db_count

    print("Polling Interval:", n_intervals)
    current_q_len = len(current_queue)

    try:
        # new_db_count = get_doc_count(cosmos_client[database][pred_collection])

        ## ALERT !!
        if (n_intervals % 50 == 0) & (n_intervals != 0):
            timestamp = dt.datetime.today()
            date = timestamp.strftime('%d-%m-%Y')
            timestamp = timestamp.strftime("Time-%H-%M-%S")
            node = 5
            alert_queue = append_alert_queue(alert_queue, timestamp, date)
            append_alertDB(node, timestamp, date)

            return [True, alert_queue]

        else:                           # Nothing changed --> Return input argument as it is
            raise PreventUpdate

    except dash.exceptions.PreventUpdate:
        pass
    except Exception as ex:
        print("TRACEBACK:", traceback.print_exc())
    finally:
        raise PreventUpdate


    """
    if new_db_count == pred_db_count: ## No ALerts. Keep displaying previous items
        print('[A] No Changes ...')
        return [True]
    elif new_db_count > pred_db_count:  ## If a new prediction has been added in COSMOS "predictions" DB. RAISE Alert
        print('[B] ALERT detected')
        pred_db_count = new_db_count

        return [False]
    print('[C]')
    return []
    """

###########     BUTTON: Human Labels Submit    ##############
@app.callback(
    Output("button-output", "children"),
    [Input("submit-sample-button", "n_clicks")],
    [
        State("human-labels", "value")
    ]
)
def button_submit(n_clicks, human_labels):
    ## Handling Initial Use-Case which always gets hit in the beginning
    if n_clicks is None:
        raise PreventUpdate
    elif n_clicks == 0:
        return []
    print("================    Button Clicked!! ", n_clicks, "   ==========================")

    ## Use-Case: User enters no labels when pressing submit
    if human_labels is None:
        return html.P("Error! Please choose options from above")

    ## Submit Labels + Meta to Cosmos DB
    final_human_labels = ";".join([lab for lab in human_labels])
    print("[0] Labels Submitted:", final_human_labels)
    labels_doc = {
    	"id" : "1",
    	"wav_name": "4D-0-0.wav",
    	"node": random.randint(1, 6),
    	"labels": final_human_labels
    }

    print(labels_doc)
    # cosmos_client[database][label_collection].insert_one(labels_doc)
    return html.P("Successfully Submitted your Feedback. Thank You!")





if __name__ == '__main__':
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    app.run_server(debug=True)
