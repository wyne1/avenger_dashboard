import dash_bootstrap_components as dbc
from pprint import pprint
import csv
import time
import pandas as pd
import librosa
from datetime import datetime

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

def append_alertDB_row(node, timestamp, name, wav_fname, footstep_pred, speech_times):
    with open('alert_db.csv', mode='a') as alert_file:
        alert_writer = csv.writer(alert_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        alert_writer.writerow([timestamp, node, False, False, name, wav_fname, footstep_pred, speech_times])

def remove_alertDB_row(sample_timestamp):
    print("Removing Sample:", sample_timestamp)
    tic = time.time()
    with open("alert_db.csv", "r") as alert_db:
        final_data = [row for row in alert_db.readlines() if sample_timestamp not in row]

    with open("alert_db.csv", "w") as alert_db:
        alert_db.writelines(final_data)
    print("[TIME] Remove Completed CSV Sample: {:.4f} sec".format(time.time()-tic))

def final_alert_press(alert_uri):
    alert_df = pd.read_csv('alert_db.csv')
    result = alert_df[alert_df['name'] == alert_uri]
    if len(result) == 0:
        return None, None, None
    # print("\t[DEBUG 1] result:", result)
    wav_fname = result['wav_fname'].values[0]
    footstep_pred = result['footstep_pred'].values[0]
    footstep_pred = [x for x in footstep_pred.split(';')]
    speech_times = result['speech_times'].values[0]
    speech_times = [int(x) for x in speech_times.split(' ')]

    return wav_fname, footstep_pred, speech_times

def extract_alert_data(input_doc):
    # y, sr = librosa.load(librosa.util.example_audio_file(), duration=10)
    print("\t INPUT Doc:", input_doc)
    doc = {}
    timestamp = datetime.fromtimestamp(int(input_doc["timestamp"]))
    doc['name'] = timestamp.strftime("Time-%H:%M:%S")
    doc['timestamp'] = str(timestamp)[:19]
    doc['node'] = input_doc["node"]
    doc['wav_fname'] = input_doc["wav_fname"]

    doc['speech_times'] = " ".join([str(x) for x in input_doc["speech_pred"]])
    doc['footstep_pred'] = input_doc["footstep_pred"]

    return doc
