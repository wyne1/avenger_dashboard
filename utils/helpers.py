import dash_bootstrap_components as dbc
from pprint import pprint
import csv
import pandas as pd

def initialize_alert_navigation():
    """
    1) Reading current UNREAD alerts from .json (on disk)
    2) Sorting based on Timestamp
    3) Returning a list for sidebar.Nav children
    """

    alert_df = pd.read_csv('alert_db.csv')
    print("Loaded Queue DF ...")
    pprint(alert_df)

    alert_links = []
    for idx, row in alert_df.iterrows():
    # for key in alert_db.keys():
        name = "Alert {}".format(row['timestamp'])
        href = "/alert-{}".format(row['timestamp'])
        alert_id = "alert-{}-link".format(row['timestamp'])
        if not row["marked"]:
            alert_links.append(dbc.NavLink(name, href=href, id=alert_id))

    return alert_links

def append_alertDB(node, timestamp, date):
    with open('alert_db.csv', mode='a') as alert_file:
        alert_writer = csv.writer(alert_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        alert_writer.writerow([timestamp, node, False, False, date])
