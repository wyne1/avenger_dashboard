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
from dash import no_update
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
from utils.helpers import append_alertDB_row, remove_alertDB_row, initialize_alert_navigation
from utils.global_utils import visualize_voice_graph

config = configparser.ConfigParser()
config.read('config.ini')

app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/brPBPO.css'],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
server = app.server

## COSMOS DB Connection + PRINTING INFO
database = config["COSMOS"]["DATABASE"]
label_collection = config["COSMOS"]["LABEL_COLLECTION"]
pred_collection = config["COSMOS"]["PREDICTION_COLLECTION"]

# tic = time.time()
# cosmos_client = MongoClient(config["COSMOS"]["URI"])
#
# print("Mongo Connection Successful. Printing Mongo Details ...")
# print(dict((db, [collection for collection in cosmos_client[db].list_collection_names()])
#              for db in cosmos_client.list_database_names()))
#
# pred_db_count = get_doc_count(cosmos_client[database][pred_collection])
# print("[COUNT] Inital DB Count:", pred_db_count)
# print("[Time Taken] ", time.time()-tic)
pred_db_count = 0

label_options = [{"label": str(LABELS[label]), "value": str(label)} for label in LABELS]

FILE = "http://localhost:8050/assets/rockstar.mp3"
PATH = "assets/rockstar.mp3"

spec_data = get_spectrogram()
speech_data = visualize_voice_graph([0,1,4,6], duration=10)

header_layout = html.Div(
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
        html.H3(
            "Data Analysis",
            className="audio_label"
        ),
        html.H6(
            "Detected Data",
            className="audio_label"
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
            style = {"padding":"30px"}
        ),
        html.Img(
            id='speech-graph',
            src="data:image/png;base64,{}".format(speech_data),
            style = {"padding":"30px"}
        )

    ],
    className="eight columns",
    id="audio_analysis"
)

audio_labelling_layout = html.Div(
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
            "ALERT",
            id="submit-sample-button",
            n_clicks=0,
            className="button_labels",
        ),
        html.Span(
            "Benign",
            id="benign-sample-button",
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
        header_layout,
        alert_toast,
        # tabs_layout,
        dbc.Container(id="info-container",
            children=[
                dbc.Row(
                    children=[
                        dbc.Col(sidebar, className="columnus"), #, width={"size": 3, "offset": 0, "order": 1}),
                        dbc.Col(audio_analysis_layout, width="auto"), #, className="flex-display", id="parent_div", width={"size": 4, "offset": 0, "order": 3}),
                        dbc.Col(audio_labelling_layout), #, className="flex-display", width={"size": 4, "offset": 0, "order": "last"})
                    ],
                ),
            ],
        ),
    ],
    className="mainContainer",
)

#########    NAVLINK: ALERT Item Click    ################
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
def append_alert_queue(alert_queue, timestamp):
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
        State("alert-queue", "children"),
        State("url", "pathname"),
    ]
)
def interval_alert(n_intervals, current_queue, alert_queue, url_path):
    """
    Tasks involced:
    (A) COSMOS ADD
        1. Ping Azure For New Predictions/Alerts
        2. RETURN
            i)  Alert Pop-Up
            ii) Navigation Bar Queue - APPEND ONLY
                If new alert, then we APPEND item to Sidebar Queue
                and reeturn the ENTIRE Queue
    (B) REFRESH from CSV
        1. Save Active State of current item in Queue
    """
    if n_intervals is None:
        raise PreventUpdate

    global FILE
    global pred_db_count

    print("======  Polling Interval:", n_intervals)
    current_q_len = len(current_queue)

    """
    new_db_count = get_doc_count(cosmos_client[database][pred_collection])
    if new_db_count == pred_db_count: ## No ALerts. Keep displaying previous items
        print('[A] No Changes ...')
        return [True]
    """

    ## COSMOS ALERT !!
    if (n_intervals % 100 == 0): # & (n_intervals != 0):
        print("[1] ALERT !!")
        timestamp = dt.datetime.today()
        name = timestamp.strftime("Time-%H:%M:%S")
        timestamp = str(timestamp)[:19]
        node = 5

        tic=time.time()
        append_alertDB_row(node, timestamp, name)
        print("[TIME] APPEND Alert to CSV:", time.time()-tic)
        update_queue = True
        print("[1] FOUND ALERT!!")
        return [True, alert_queue]

    ##  Frequent Update of LINKS
    elif (n_intervals % 2 == 0):
        print("[2] UPDATING Queue Naturally ...")

        target_idx, _ = find_alert_press(current_queue, url_path)
        print('Active IDX:', target_idx)
        updated_div = dbc.Nav(
            initialize_alert_navigation(active=target_idx),
            vertical=True,
            pills=True,
            justified=True,
            id="current_queue"
        )
        # updated_queue = initialize_alert_navigation()
        # print("[2] Updating Queue")

        return [False, [updated_div]]

    else:
        print("[3] NO Interval Update")
        return [False, no_update]

    print("[-99] WHAT NOW!!")
    # except dash.exceptions.PreventUpdate:
    #     pass
    # except Exception as ex:
    #     print("TRACEBACK:", traceback.print_exc())
    #     raise PreventUpdate

    # print(">> WHAT NOW !!")


###########     BUTTON: Human Labels Submit    ##############
def find_next_alert(current_q, target_url):
    target_idx, next_url = -1, "/"
    len_alert_queue = len(current_q)

    for i, item in enumerate(current_q):
        if target_url == item["props"]["href"]:
            print("\t FOUND NEXT ALERT: ", i, len_alert_queue, target_url, item["props"]["href"])
            if i < len_alert_queue-1:
                target_idx = i + 1
                next_url = current_q[i+1]["props"]['href']
            elif i == len_alert_queue-1:
                target_idx = i - 1
                next_url = current_q[i-1]["props"]['href']


    return target_idx, next_url

@app.callback(
    [Output("button-output", "children"), Output("url", "pathname")],
    [Input("submit-sample-button", "n_clicks")],
    [
        State("human-labels", "value"),
        State("url", "pathname"),
        State("current_queue", "children")
    ]
)
def button_submit(n_clicks, human_labels, url, current_queue):
    ## Handling Initial Use-Case which always gets hit in the beginning
    if n_clicks is None:
        raise PreventUpdate
    elif n_clicks == 0:
        raise PreventUpdate
    print("================    Button Clicked!! ", n_clicks, "   ==========================")

    ## Use-Case: User enters no labels when pressing submit
    if human_labels is None:
        return [html.P("Error! Please choose options from above"), no_update]

    if "alert" in url:
        current_alert = url.split("alert-")[-1]
    print("Current URL:", current_alert)

    target_idx, next_url = find_next_alert(current_queue, url)
    print(target_idx, next_url)

    ## Submit Labels + Meta to Cosmos DB
    final_human_labels = ";".join([lab for lab in human_labels])
    print("[0] Labels Submitted:", final_human_labels)
    labels_doc = {
        "id" : "1",
        "wav_name": "4D-0-0.wav",
        "node": random.randint(1, 6),
        "labels": final_human_labels
    }
    # cosmos_client[database][label_collection].insert_one(labels_doc)

    remove_alertDB_row(current_alert)

    print(labels_doc)

    return [html.P("Successfully Submitted your Feedback. Thank You!"), next_url]



if __name__ == '__main__':
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    app.run_server(debug=True)
