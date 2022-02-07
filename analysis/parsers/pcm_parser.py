import pandas as pd

from datetime import datetime, tzinfo
from dateutil import tz
from utils.utils import get_pcm_tzinfo

def get_csv(node_name, logfile, experiment_dirname):
    raw_csv = pd.read_csv(logfile)
    raw_csv.drop(columns=['Unnamed: 594'], inplace=True)

    labels = raw_csv.iloc[0]
    old_cols_name = [x.split('.')[0] for x in list(labels.keys())]      # Removing the .1, .2, etc. Now only contains classification of data, like, System, Core 0, etc.
    labels = list(labels.values)                                       # List with all the attributes of data
    new_cols_name = [old_cols_name[i] + " " + labels[i]  for i in range(len(old_cols_name))]
    column_change_dict = {raw_csv.columns.values[i]: new_cols_name[i] for i in range(len(new_cols_name))}

    raw_csv.rename(columns=column_change_dict, inplace=True)
    raw_csv.drop(index=raw_csv.index[0], axis=0, inplace=True)
    timestamp = raw_csv['System Date'] + " " + raw_csv['System Time']
    raw_csv.insert(0,'Timestamp', timestamp)
    raw_csv.drop(labels=['System Date', 'System Time'], axis=1, inplace=True)

    node_tzinfo = get_pcm_tzinfo(experiment_dirname, node_name)
    print(node_tzinfo)

    raw_csv['Timestamp'] = raw_csv.apply(lambda r: datetime.fromisoformat(r['Timestamp']), axis=1)
    with_timezone = [x.replace(tzinfo=tz.gettz(node_tzinfo)) for x in raw_csv['Timestamp']]
    raw_csv['Timestamp'] = with_timezone
    raw_csv['Node Name'] = [node_name] * raw_csv.shape[0]
    return raw_csv