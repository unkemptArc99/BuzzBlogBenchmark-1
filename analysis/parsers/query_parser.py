import datetime
import re

from .base_parser import BaseParser

# Constants
QUERY_LOG_PATTERN = r"^\[(.+)\] pid=(.+) tid=(.+) request_id=(.+) latency=(.+) query=\"(.+)\"$"


class QueryParser(BaseParser):
    def __init__(self, logfile):
        super().__init__(logfile)

    def parse(self):
        data = {"timestamp": [], "request_id": [], "dbname": [], "type": [], "latency": []}
        for log in self._logfile:
            log_match = re.match(QUERY_LOG_PATTERN, log.decode("utf-8"))
            if log_match:
                timestamp, _, _, request_id, latency, query_str = log_match.groups()
                query_type = query_str.strip().split()[0].upper()
                if query_type == "SELECT":
                    dbname = re.findall(r"[Ff][Rr][Oo][Mm]\s+(\w+)", query_str)[0]
                elif query_type == "INSERT":
                    dbname = re.findall(r"[Ii][Nn][Tt][Oo]\s+(\w+)", query_str)[0]
                elif query_type == "UPDATE":
                    dbname = re.findall(r"[Uu][Pp][Dd][Aa][Tt][Ee]\s+(\w+)", query_str)[0]
                elif query_type == "DELETE":
                    dbname = re.findall(r"[Ff][Rr][Oo][Mm]\s+(\w+)", query_str)[0]
                else:
                    dbname = None
                data["timestamp"].append(datetime.datetime.strptime(timestamp[:-3], "%Y-%m-%d %H:%M:%S.%f"))
                data["request_id"].append(request_id)
                data["type"].append(query_type)
                data["latency"].append(float(latency) * 1000)
                data["dbname"].append(dbname)
        return data
