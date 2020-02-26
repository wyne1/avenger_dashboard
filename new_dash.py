# Import required libraries
import time
import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import os
import numpy as np
import random
import configparser
from pymongo import MongoClient

from utils.mongo_utils import get_doc_count
from utils.visuals import get_spectrogram
from controls import LABELS

config = configparser.ConfigParser()
config.read('config.ini')

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

## COSMOS DB Connection + PRINTING INFO
database = config["COSMOS"]["DATABASE"]
label_collection = config["COSMOS"]["LABEL_COLLECTION"]
pred_collection = config["COSMOS"]["PREDICTION_COLLECTION"]

tic = time.time()
cosmos_client = MongoClient(config["COSMOS"]["URI"])

print("Mongo Connection Successful. Printing Mongo Details ...")
print(dict((db, [collection for collection in cosmos_client[db].list_collection_names()])
             for db in cosmos_client.list_database_names()))

pred_db_count = get_doc_count(cosmos_client[database][pred_collection])
print("[COUNT] Inital DB Count:", pred_db_count)
print("[Time Taken] ", time.time()-tic)

label_options = [{"label": str(LABELS[label]), "value": str(label)} for label in LABELS]

FILE = "http://localhost:8050/assets/rockstar.mp3"
PATH = "assets/rockstar.mp3"

spec_data = get_spectrogram()

app.layout = html.Div(
    [
        dcc.Interval(id="interval-updating-alert", interval=2000, n_intervals=0),
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
        State("human-labels", "value")
    ]
)
def button_submit(n_clicks, human_labels):

    print("================    Button Clicked!! ", n_clicks, "   ==========================")
    ## Handling Initial Use-Case which always gets hit in the beginning
    if n_clicks == 0:
        return []

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
    cosmos_client[database][label_collection].insert_one(labels_doc)
    return html.P("Successfully Submitted your Feedback. Thank You!")

####  CALLBACK: INTERVAL updating UI according to new sample
# @app.callback(
#     [Output("wav-player", "src"), Output("spectrogram", "src"), Output("ai-preds", "value")],
#     [Input("interval-updating-alert", "n_intervals")],
# )
# def interval_alert(n_intervals):
#     global FILE
#     global pred_db_count
#     new_db_count = get_doc_count(cosmos_client[database][pred_collection])
#
#
#     if new_db_count == pred_db_count: ## No ALerts. Keep displaying previous items
#         print('[A] No Changes ...')
#         return [FILE, "data:image/png;base64,{}".format(get_spectrogram()), []]
#     elif new_db_count > pred_db_count:  ## If a new prediction has been added in COSMOS "predictions" DB. RAISE Alert
#         print('[B] ALERT detected')
#         pred_db_count = new_db_count
#         wav_audio = FILE
#         spec_image = "data:image/png;base64,{}".format(get_spectrogram())
#         predictions = ["footsteps", "speech"]
#
#         return [wav_audio, spec_image, predictions]
#     print('[C]')
#     return []




if __name__ == '__main__':
    app.run_server(debug=True)
