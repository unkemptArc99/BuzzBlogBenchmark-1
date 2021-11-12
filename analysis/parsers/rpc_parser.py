import datetime
import re

from .base_parser import BaseParser

# Constants
RPC_LOG_PATTERN = r"^\[(.+)\] pid=(.+) tid=(.+) request_id=(.+) server=(.+) function=(.+) latency=(.+)$"


class RPCParser(BaseParser):
    def __init__(self, logfile):
        super().__init__(logfile)

    def parse(self):
        data = {"timestamp": [], "request_id": [], "server": [], "function": [],
                "latency": []}
        for log in self._logfile:
            log_match = re.match(RPC_LOG_PATTERN, log.decode("utf-8"))
            if log_match:
                timestamp, _, _, request_id, server, function, latency = log_match.groups()
                data["timestamp"].append(datetime.datetime.strptime(timestamp[:-3], "%Y-%m-%d %H:%M:%S.%f"))
                data["request_id"].append(request_id)
                data["server"].append(server)
                data["function"].append(function)
                data["latency"].append(float(latency) * 1000)
        return data