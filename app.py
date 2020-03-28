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
import librosa
import matplotlib
matplotlib.use('Agg')
import pandas as pd
from utils.mongo_utils import get_doc_count, get_alert_doc
from utils.visuals import get_spectrogram
from controls import LABELS
from utils.sidebar import sidebar
import datetime as dt
from utils.helpers import append_alertDB_row, remove_alertDB_row, initialize_alert_navigation, extract_alert_data, final_alert_press
from utils.helpers import generate_markdown_text
from utils.global_utils import visualize_voice_graph
# from flask_caching import Cache
from threading import Lock

from utils.blob_storage import init_azure_storage, download_blob
from plotly import graph_objs as go
from plotly.graph_objs import *
from pages import page1, page2
config = configparser.ConfigParser()
config.read('config.ini')

# DEBUG = config["MISC"]["DEBUG"]


app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/brPBPO.css'],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

app.config.suppress_callback_exceptions = True
server = app.server
lock = Lock()

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

df = pd.read_csv("data/new_data.csv",
    dtype=object,
)

df1 = pd.read_csv("data/new_data1.csv",
    dtype=object,
)


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

## COSMOS DB Connection + PRINTING INFO
database = config["COSMOS"]["DATABASE"]
label_collection = config["COSMOS"]["LABEL_COLLECTION"]
pred_collection = config["COSMOS"]["PREDICTION_COLLECTION"]

tic = time.time()
cosmos_client = MongoClient(config["COSMOS"]["URI"])

print("Mongo Connection Successful. Printing Mongo Details ...")
# print(dict((db, [collection for collection in cosmos_client[db].list_collection_names()])
#              for db in cosmos_client.list_database_names()))

# pred_db_count = get_doc_count(cosmos_client[database][pred_collection])
# print("[-2] Time Taken ", time.time()-tic)
# print("\t[COUNT] Inital DB Count:", pred_db_count)
pred_db_count = 6

tic = time.time()
RESOURCE_GROUP = config['BLOB']['RESOURCE_GROUP']
STORAGE_ACCOUNT = config['BLOB']['STORAGE_ACCOUNT']
ACCOUNT_KEY = config['BLOB']['ACCOUNT_KEY']
CONNECTION_STR = config['BLOB']['CONNECTION_STRING']
az_storage_client = init_azure_storage(RESOURCE_GROUP, STORAGE_ACCOUNT, ACCOUNT_KEY, method='sas')
print("[-1] Time Taken init_azure_storage() {:.4f} sec".format(time.time()-tic))

label_options = [{"label": str(LABELS[label]), "value": str(label)} for label in LABELS]

FILE = "http://127.0.0.1:8050/assets/temp.wav"

spec_data, duration = get_spectrogram("assets/temp.wav")
speech_data = visualize_voice_graph([1, 2, 6, 7.5], duration=10)


app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content")
    ]
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/forest-avenger/page2":
        return page2.create_layout(app)
    else:
        return page1.create_layout(app)


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
    [Output("current-queue", "children"), Output("ai-preds", "value"), Output("wav-player", "src"),
        Output("spectrogram", "src"), Output("speech-graph", "src"), Output("alert-markdown", "children")],
    [Input("url", "pathname")],
    [State("current-queue", "children")]
)
def alert_item_button(url_path, current_q):
    """
    1) Change LINK Active Status
    2) Update Alert Details (WAV, Spec, ai-preds)
    """
    try:
        print("ALERT Item PRESSED: ", url_path)
        current_alert = None
        if "alert" in url_path:
            current_alert = url_path.split("alert-")[-1]
        print("Current FNAME:", current_alert)
        target_idx, final_q = find_alert_press(current_q, url_path)

        if target_idx == -1:
            print("Target URL not FOUND!")
            ai_preds = ["cricket", "birds"]
            return [current_q, no_update, no_update, no_update, no_update, no_update]
        else:
            wav_fname, ai_preds, speech_times, node, timestamp = final_alert_press(current_alert)
            print("\t[DEBUG 2]: ", wav_fname, ai_preds, speech_times)
            wav_path = "assets/{}".format(wav_fname)
            wav_src_path = "http://localhost:8050/assets/{}".format(wav_fname)
            # print("DEBUG isFile:", os.listdir("http://localhost:8050/assets"))

            spec_data, duration = get_spectrogram(wav_path)
            print("\tGOT SPECTROGRAM", len(spec_data))
            speech_data = visualize_voice_graph(speech_times, duration=duration)
            print("\tGOT Speech Graph", len(speech_data))
            return [final_q, ai_preds, wav_src_path, spec_data, speech_data, generate_markdown_text(node, timestamp)]
    except:
        print(traceback.print_exc())
        raise PreventUpdate



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
        State("current-queue", "children"),
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

    global pred_db_count

    print("===================     Polling Interval:", n_intervals, "   ===================")
    current_q_len = len(current_queue)

    ## COSMOS ALERT !!
    new_db_count = get_doc_count(cosmos_client[database][pred_collection])
    if new_db_count > pred_db_count:
    # if (n_intervals % 100 == 0): # & (n_intervals != 0):
        num_new_samples = new_db_count - pred_db_count
        print("[1] ALERT !!  # New Samples: {}".format(num_new_samples))

        alert_docs = get_alert_doc(cosmos_client[database][pred_collection], num_new_samples)

        # alert_doc = []
        for doc in alert_docs:
            doc = extract_alert_data(doc)
            print("Returning DOC:", doc)
            wav = download_blob(az_storage_client, 'temp-cont', doc['wav_fname'])
            with open('assets/{}'.format(doc['wav_fname']), "wb") as my_blob:
                my_blob.write(wav)

            # timestamp = dt.datetime.today()
            # name = timestamp.strftime("Time-%H:%M:%S")
            # timestamp = str(timestamp)[:19]
            # node = 5

            append_alertDB_row(doc['node'], doc['timestamp'], doc['name'], doc['wav_fname'], doc['footstep_pred'], doc['speech_times'])
            with lock:
                pred_db_count = new_db_count

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
            id="current-queue"
        )
        # updated_queue = initialize_alert_navigation()
        # print("[2] Updating Queue")

        return [False, [updated_div]]

    ## No ALerts. Keep displaying previous items
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
        State("current-queue", "children")
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

    current_alert = None
    if "alert" in url:
        current_alert = url.split("alert-")[-1]
    print("Current URL:", current_alert)

    target_idx, next_url = find_next_alert(current_queue, url)
    print(target_idx, next_url)

    wav_fname, _, _, node = final_alert_press(current_alert)

    ## Submit Labels + Meta to Cosmos DB
    final_human_labels = ";".join([lab for lab in human_labels])
    print("[0] Labels Submitted:", final_human_labels)
    labels_doc = {
        # "id" : "1",
        "wav_name": wav_fname,
        "node": node,
        "labels": final_human_labels
    }
    cosmos_client[database][label_collection].insert_one(labels_doc)
    remove_alertDB_row(current_alert)
    # Todo: REMOVE wav_fname WAV file

    print(labels_doc)
    return [html.P("Successfully Submitted your Feedback. Thank You!"), next_url]


#### PAGE 2 CALLBACKS ####
daysInMonth = [30, 31, 30, 31, 31, 30]

# Get index for the specified month in the dataframe
monthIndex = pd.Index(["Apr", "May", "June", "July", "Aug", "Sept"])

colorVal = [
    "#F4EC15",
    "#DAF017",
    "#BBEC19",
    "#9DE81B",
    "#80E41D",
    "#66E01F",
    "#4CDC20",
    "#34D822",
    "#24D249",
    "#25D042",
    "#26CC58",
    "#28C86D",
    "#29C481",
    "#2AC093",
    "#2BBCA4",
    "#2BB5B8",
    "#2C99B4",
    "#2D7EB0",
    "#2D65AC",
    "#2E4EA4",
    "#2E38A4",
    "#3B2FA0",
    "#4E2F9C",
    "#603099",
]
# @app.callback(
#     Output("histogram", "figure"),
# )
def get_hist1_selection(selectedLocation):
    print("Here")
    global colorVal
    xVal = []
    yVal = []
    xSelected = []

    # for i in range()


# FOR HISTOGRAM
def get_selection(month, day, selection):
    xVal = []
    yVal = []
    global colorVal
    xSelected = []


    # Put selected times into a list of numbers xSelected
    xSelected.extend([int(x) for x in selection])
    print("sadasdasd",xSelected)
    for i in range(24):
        # If bar is selected then color it white
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = "#FFFFFF"
        xVal.append(i)
        # Get the number of rides at a particular time
        yVal.append(len(totalList[month][day][totalList[month][day].index.hour == i]))
    return [np.array(xVal), np.array(yVal), np.array(colorVal)]

@app.callback(
    Output("bar-selector", "value"),
    [Input("histogram", "selectedData"), Input("histogram", "clickData")],
)
def update_bar_selector(value, clickData):
    holder = []
    if clickData:
        holder.append(str(int(clickData["points"][0]["x"])))
    if value:
        for x in value["points"]:
            holder.append(str(int(x["x"])))
    return list(set(holder))


# Clear Selected Data if Click Data is used
@app.callback(Output("histogram", "selectedData"), [Input("histogram", "clickData")])
def update_selected_data(clickData):
    if clickData:
        return {"points": []}


# Update the total number of rides Tag
# @app.callback(Output("total-rides", "children"), [Input("date-picker", "date")])
# def update_total_rides(datePicked):
#     date_picked = dt.strptime(datePicked, "%Y-%m-%d")
#     return "Total Number of rides: {:,d}".format(
#         len(totalList[date_picked.month - 4][date_picked.day - 1])
#     )

# Update Histogram Figure based on Month, Day and Times Chosen

@app.callback(
    Output("histogram1", "figure"),
)
def update_histogram2( selectedLocation):
    print("Histogram2 Function")




@app.callback(
    Output("histogram", "figure"),
    [Input("date-picker", "date"), Input("bar-selector", "value")],
)
def update_histogram(datePicked, selection):
    print("UPDATE HISTOGRAM")

    print(selection)
    date_picked = dt.datetime.strptime(datePicked, "%Y-%m-%d")
    monthPicked = date_picked.month - 4
    dayPicked = date_picked.day - 1

    print("Date Picked: {}\tMonth Picked: {}\tDay Picked:{}".format(date_picked, monthPicked, dayPicked))
    [xVal, yVal, colorVal] = get_selection(monthPicked, dayPicked, selection)
    print(xVal, yVal)


    layout = go.Layout(
        title= "CHECKING HISTOGRAM",
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        xaxis=dict(
            range=[-0.5, 23.5],
            showgrid=False,
            nticks=25,
            fixedrange=True,
            ticksuffix=":00",
        ),
        yaxis=dict(
            range=[0, max(yVal) + max(yVal) / 4],
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        ),
        annotations=[
            dict(
                x=xi,
                y=yi,
                text=str(yi),
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(color="white"),
            )
            for xi, yi in zip(xVal, yVal)
        ],
    )

    return go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker=dict(color=colorVal), hoverinfo="x"),
            go.Scatter(
                opacity=0,
                x=xVal,
                y=yVal / 2,
                hoverinfo="none",
                mode="markers",
                marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
                visible=True,
            ),
        ],
        layout=layout,
    )

def getLatLonColor(selectedData, month, day):
    print("MONTH: {} | DAY: {}".format(month, day))
    listCoords = totalList[month][day]

    # No times selected, output all times for chosen month and date
    if selectedData is None or len(selectedData) is 0:
        return listCoords
    listStr = "listCoords["
    for time in selectedData:
        if selectedData.index(time) is not len(selectedData) - 1:
            listStr += "(totalList[month][day].index.hour==" + str(int(time)) + ") | "
        else:
            listStr += "(totalList[month][day].index.hour==" + str(int(time)) + ")]"
    return eval(listStr)



@app.callback(
    Output("map-graph", "figure"),
    [
        Input("date-picker", "date"),
        Input("bar-selector", "value"),
    ],
)
def update_graph(datePicked, selectedData):
    zoom = 16
    latInitial = 33.732570
    lonInitial = 73.036011
    bearing = 0

    date_picked = dt.datetime.strptime(datePicked, "%Y-%m-%d")
    monthPicked = date_picked.month - 4
    dayPicked = date_picked.day - 1
    # listCoords = getLatLonColor(selectedData, monthPicked, dayPicked)

    return go.Figure(
        data=[
            # Plot of important locations on the map
            Scattermapbox(
                lat=[list_of_locations[i]["lat"] for i in list_of_locations],
                lon=[list_of_locations[i]["lon"] for i in list_of_locations],
                mode="markers",
                hoverinfo="lat+lon+text",
                text=[i for i in list_of_locations],
                marker=dict(size=12, color="#7BEC97"),
            ),
        ],
        layout=Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=35, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=latInitial, lon=lonInitial),  # 40.7272  # -73.991251
                style="satellite-streets", #"""'light', 'basic', 'outdoors', 'satellite', or 'satellite-streets' """
                bearing=bearing,
                zoom=zoom,
            ),
            updatemenus=[
                dict(
                    buttons=(
                        [
                            dict(
                                args=[
                                    {
                                        "mapbox.zoom": 12,
                                        "mapbox.center.lon": "-73.991251",
                                        "mapbox.center.lat": "40.7272",
                                        "mapbox.bearing": 0,
                                        "mapbox.style": "dark",
                                    }
                                ],
                                label="Reset Zoom",
                                method="relayout",
                            )
                        ]
                    ),
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
        ),
    )

if __name__ == '__main__':
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    app.run_server(debug=True)
