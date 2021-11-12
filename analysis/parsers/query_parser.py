import datetime
import re

from .base_parser import BaseParser

# Constants
QUERY_LOG_PATTERN = r"^\[(.+)\] pid=(.+) tid=(.+) request_id=(.+) dbname=(.+) latency=(.+) query=\"(.+)\"$"


class QueryParser(BaseParser):
    def __init__(self, logfile):
        super().__init__(logfile)

    def parse(self):
        data = {"timestamp": [], "request_id": [], "dbname": [], "type": [], "latency": []}
        for log in self._logfile:
            log_match = re.match(QUERY_LOG_PATTERN, log.decode("utf-8"))
            if log_match:
                timestamp, _, _, request_id, dbname, latency, query_str = log_match.groups()
                data["timestamp"].append(datetime.datetime.strptime(timestamp[:-3], "%Y-%m-%d %H:%M:%S.%f"))
                data["request_id"].append(request_id)
                data["dbname"].append(dbname)
                data["type"].append(query_str.strip().split()[0].upper())
                data["latency"].append(float(latency) * 1000)
        return data