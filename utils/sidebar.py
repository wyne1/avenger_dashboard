"""
This app creates a collapsible, responsive sidebar layout with
dash-bootstrap-components and some custom css with media queries.

When the screen is small, the sidebar moved to the top of the page, and the
links get hidden in a collapse element. We use a callback to toggle the
collapse when on a small screen, and the custom CSS to hide the toggle, and
force the collapse to stay open when the screen is large.

dcc.Location is used to track the current location. There are two callbacks,
one uses the current location to render the appropriate page content, the other
uses the current location to toggle the "active" properties of the navigation
links.

For more details on building multi-page Dash applications, check out the Dash
documentation: https://dash.plot.ly/urls
"""
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from utils.helpers import initialize_alert_navigation


# we use the Row and Col components to construct the sidebar header
# it consists of a title, and a toggle, the latter is hidden on large screens
sidebar_header = html.Div(
    [
        html.H2("Alerts", className="display-4", style={"align": "center"}),
            # the column containing the toggle will be only as wide as the
            # toggle, resulting in the toggle being right aligned
            # width="auto"## width={"size": 3, "offset": 0, "order": 1}, # auto/True
            # vertically align the toggle in the center
            # align="center",
    ]
)

sidebar = html.Div(
    [
        sidebar_header,
        # we wrap the horizontal rule and short blurb in a div that can be
        # hidden on a small screen
        html.Div(
            [
                html.Hr(),
                html.P(
                    "Alerts will be shown below as they occur in Real-Time",
                    className="alert-text",
                ),
            ],
            id="blurb",
        ),
        # use the Collapse component to animate hiding / revealing links
        html.Div(
            dbc.Nav(
                initialize_alert_navigation(),
                # [
                #     dbc.NavLink("Alert 1", href="/alert-1", id="alert-1-link", active=True),
                #     dbc.NavLink("Alert 2", href="/alert-2", id="alert-2-link"),
                # ],
                vertical=True,
                pills=True,
                justified=True,
                id="current_queue"
            ),
            id="alert-queue",
        ),
    ],
    id="sidebar",
)

if __name__ == '__main__':
    app = dash.Dash(
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        # these meta_tags ensure content is scaled correctly on different devices
        # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
    )

    app.layout = sidebar
    app.run_server(debug=True)
