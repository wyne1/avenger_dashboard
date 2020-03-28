import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from controls import LABELS
from utils.sidebar import sidebar
from utils.helpers import generate_markdown_text
from utils.global_utils import visualize_voice_graph
from utils.visuals import get_spectrogram
from controls import LABELS

spec_data, duration = get_spectrogram("assets/temp.wav")
speech_data = visualize_voice_graph([1, 2, 6, 7.5], duration=10)
label_options = [{"label": str(LABELS[label]), "value": str(label)} for label in LABELS]


def create_layout(app):
    FILE = "http://127.0.0.1:8050/assets/temp.wav"
    header_layout = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                    [
                        html.Img(
                            src=app.get_asset_url("forest-nobg.png"),
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
                            "Forest Avenger Dashboard",
                        ),

                        html.H5(
                            ["The Forests Initiate"],
                        )

                    ], width=6, className="col-md", style = {"text-align": "center"}),

                    dbc.Col(
                    [
                        # dbc.Button("GitHub Page", href="https://github.com/abdylan/audioAnn_GUI", color="secondary", className="mr-1", size="lg", id="button")
                        html.A(
                            html.Button("GitHub Page", id="learn-more-button"),
                            href="https://github.com/abdylan/audioAnn_GUI",
                        )
                    ], width = 3, className="col-sm")
                ], className = "row justify-content-end")
        ], style={"width": "100%", "margin-left": "3%"},
    )

    tabs_layout = html.Div(
        [
            dbc.Col(
                [
                    # dbc.NavItem(dbc.NavLink("Active", active=True, href="#")),
                    # dbc.NavLink("A link", href="#"),
                    dcc.Link("Audio Analysis", href="/forest-avenger/page1"),
                    dcc.Link("Event History", href="/forest-avenger/page2"),
                ],
                id="tabs",
                className="row tabs",
            ),
        ], style = {"width": "100%", "padding-left": "3%"}
    )

    audio_analysis_layout = html.Div(
        [
            dbc.Col([
                dcc.Markdown(
                    generate_markdown_text(-99, "1999-00-00 00:00"),
                    className="audio_label",
                    id="alert-markdown"
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
                    src=spec_data,
                    ),
                html.Img(
                    id='speech-graph',
                    src=speech_data,
                    style={"padding":"30px"}
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
                dbc.Row([
                    dbc.Col([
                        html.Span(
                            "Benign",
                            id="benign-sample-button",
                            n_clicks=0,
                            className="button_labels",
                        ),
                    ]),
                    dbc.Col([
                        html.Span(
                            "Submit",
                            id="submit-sample-button",
                            n_clicks=0,
                            className="button_labels",
                        ),
                    ]),
                ]),
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



    return html.Div(
        [
            dcc.Interval(id="interval-updating-alert", interval=5000, n_intervals=0),
            dcc.Location(id="url"),

            dbc.Col([sidebar, alert_toast], width = 2),
            dbc.Col(
            [
                dbc.Row([header_layout]),
                html.Br(),
                dbc.Row([tabs_layout]),
                dbc.Row([
                    dbc.Col([
                        audio_analysis_layout
                    ], width = 7),
                    dbc.Col([
                        audio_labelling_layout
                    ], width = 5),

                ], id = "audio_row"),
            ], width = 12)
        ], className = "main_div",
    )
