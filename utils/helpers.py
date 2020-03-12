import dash_bootstrap_components as dbc
from pprint import pprint
import csv
import time
import pandas as pd

def initialize_alert_navigation(active=None):
    """
    1) Reading current UNREAD alerts from .json (on disk)
    2) Sorting based on Timestamp
    3) Returning a list for sidebar.Nav children
    """

    alert_df = pd.read_csv('alert_db.csv')
    print("Loaded Queue DF | Shape: {}".format(alert_df.shape))
    print("Current Active IDX:", active, type(active))
    alert_links = []
    for idx, row in alert_df.iterrows():
    # for key in alert_db.keys():
        row_name = row['name']
        name = "Alert {}".format(row_name)
        href = "/alert-{}".format(row_name)
        alert_id = "alert-{}-link".format(row_name)
        active_value = False
        # print("[DEBUG] Idx: {}  | Href: {}  |  Name: {}".format(idx, href, name))
        # print("\tIF COND", (isinstance(active, int)), (active is idx))
        if (isinstance(active, int)) & (active is idx):
            # print("\tFOUND active IDX")
            active_value = True
        if not row["marked"]:
            alert_links.append(dbc.NavLink(name, href=href, id=alert_id, active=active_value))

    return alert_links

def append_alertDB_row(node, timestamp, name):
    with open('alert_db.csv', mode='a') as alert_file:
        alert_writer = csv.writer(alert_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        alert_writer.writerow([timestamp, node, False, False, name])

def remove_alertDB_row(sample_timestamp):
    print("Removing Sample:", sample_timestamp)
    tic = time.time()
    with open("alert_db.csv", "r") as alert_db:
        final_data = [row for row in alert_db.readlines() if sample_timestamp not in row]

    with open("alert_db.csv", "w") as alert_db:
        alert_db.writelines(final_data)
    print("[TIME] Remove Completed CSV Sample: {:.4f} sec".format(time.time()-tic))
