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

label_options = [{"label": str(LABELS[label]), "value": str(label)} for label in LABELS]

df = pd.read_csv("new_data.csv",
    dtype=object,
)

df1 = pd.read_csv("new_data1.csv",
    dtype=object,
)


mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

# df = pd.concat([df1,df2,df3], axis=0)
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

print(node_dict)
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

hist_layout = go.Layout(
    title= "CHECKING HISTOGRAM",
    bargap=0.1,
    bargroupgap=0.1,
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
            children = [
                # Four Columns
                html.Div(
                    className="six columns div-user-controls",
                    # children=[
                    #     ],
                ),
                html.Div(
                    className="six columns div-for-charts bg-grey",
                    children=[
                        html.Div(
                            className="text-padding",
                            children=[
                                "Locations of all the Avenger Nodes"
                            ],
                        ),
                        dcc.Graph(id="map-graph"),

                    ],
                ),
            ],
        ),

        html.Div(
            className="row",
            children=[

                html.Div(
                    className="six columns div-for-charts bg-grey",
                    children=[
                        html.Div(
                            className="text-padding",
                            children=[
                                "Events in Every Node"
                            ],
                        ),
                        dcc.Graph(
                            id="histogram1",
                            figure={
                                'data': [
                                    {'x': node_list, 'y': node_freq, 'type': 'bar', 'name': 'Nodes'}
                                ],
                                'layout': hist_layout
                            }

                        ),

                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                html.P(
                                    """Select Node and Date for Alert History"""
                                ),
                                # Dropdown for locations on map
                                dcc.Dropdown(
                                    id="location-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in list_of_locations
                                    ],
                                    placeholder="Select a location",
                                )
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="six columns div-for-charts bg-grey",
                    children=[
                        html.Div(
                            className="text-padding",
                            children=[
                                "Events on the specific Data Time"
                            ],
                        ),
                        dcc.Graph(id="histogram"),
                        html.P(
                            """Select different days using the date picker or by selecting
                            different time frames on the histogram."""
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    min_date_allowed=dt(2014, 4, 1),
                                    max_date_allowed=dt(2014, 9, 30),
                                    initial_visible_month=dt(2014, 4, 1),
                                    date=dt(2014, 4, 1).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[

                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown to select times
                                        dcc.Dropdown(
                                            id="bar-selector",
                                            options=[
                                                {
                                                    "label": str(n) + ":00",
                                                    "value": str(n),
                                                }
                                                for n in range(24)
                                            ],
                                            multi=True,
                                            placeholder="Select certain hours",
                                        )
                                    ],
                                ),
                            ],
                        ),
                        # Html.Div(
                        #
                        # ),
                        # html.P(id="total-rides"),
                        # html.P(id="total-rides-selection"),
                        # html.P(id="date-value"),

                    ],
                ),

            ],
        ),
    ],
    className="mainContainer",
)

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
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
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

    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
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
    app.run_server(debug=True)
