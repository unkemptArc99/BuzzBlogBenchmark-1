import datetime
import re

import pandas as pd

from .base_parser import BaseParser

# Constants
HW_METRICS = {
    "cpu": ["user", "nice", "system", "wait", "irq", "soft", "steal", "idle", "total", "guest", "guest_n", "intrpt"],
    "mem": ["used", "free", "slab", "mapped", "anon", "anonh", "inactive", "hits"],
    "dsk": ["reads", "rmerge", "rkbytes", "waitr", "writes", "wmerge", "wkbytes", "waitw", "request", "quelen", "wait",
            "svctim", "util"]
}


class CollectlParser(BaseParser):
    def __init__(self, logfile, hw_type, start_time=None, end_time=None):
        super().__init__(logfile)
        self._hw_type = hw_type
        self._start_time = start_time
        self._end_time = end_time

    def parse(self):
        data = {"hw_no": [], "timestamp": [], "hw_metric": [], "value": []}
        for log in self._logfile:
            if log[0] == '#':
                timezone = re.findall(r"TZ: ([-+]\d{4})", log)
                if timezone:
                    offset = datetime.timedelta(hours=(1 if timezone[0][0] == '+' else -1) * int(timezone[0][1:3]))
                # Skip comments.
                continue
            log_entry = log.split()
            timestamp = datetime.datetime.strptime(" ".join(log_entry[:2]), "%Y%m%d %H:%M:%S.%f") - offset
            if (self._start_time and pd.Timestamp(timestamp) < pd.Timestamp(self._start_time)) or (self._end_time and pd.Timestamp(timestamp) > pd.Timestamp(self._end_time)):
                continue
            for hw_no in range((len(log_entry) - 2) // len(HW_METRICS[self._hw_type])):
                for (i, hw_metric) in enumerate(HW_METRICS[self._hw_type]):
                    data["hw_no"].append(hw_no)
                    data["timestamp"].append(timestamp)
                    data["hw_metric"].append(hw_metric)
                    data["value"].append(log_entry[i + 2 + hw_no * len(HW_METRICS[self._hw_type])])
        return data
