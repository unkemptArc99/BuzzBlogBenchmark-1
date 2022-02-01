import pandas as pd

def get_csv(node_name, logfile):
    raw_csv = pd.read_csv(logfile)
    raw_csv.drop(columns=['Unnamed: 594'], inplace=True)
    raw_csv.insert()