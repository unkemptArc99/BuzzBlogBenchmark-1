import datetime
import re

from .base_parser import BaseParser

# Constants
REDIS_LOG_PATTERN = r"^\[(.+)\] pid=(.+) tid=(.+) request_id=(.+) latency=(.+) service_name=(.+) command=(.+)$"


class RedisParser(BaseParser):
    def __init__(self, logfile):
        super().__init__(logfile)

    def parse(self):
        data = {"timestamp": [], "request_id": [], "latency": [], "service_name": [], "command": []}
        for log in self._logfile:
            log_match = re.match(REDIS_LOG_PATTERN, log.decode("utf-8"))
            if log_match:
                timestamp, _, _, request_id, latency, service_name, command = log_match.groups()
                data["timestamp"].append(datetime.datetime.strptime(timestamp[:-3], "%Y-%m-%d %H:%M:%S.%f"))
                data["request_id"].append(request_id)
                data["latency"].append(float(latency) * 1000)
                data["service_name"].append(service_name)
                data["command"].append(command)
        return data