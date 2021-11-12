import datetime
import re

from .base_parser import BaseParser

# Constants
REQUEST_LOG_PATTERN = r"^\[(\d+\-\d+\-\d+ \d+:\d+:\d+.\d+)\] (.+) (.+) (\d+) - latency=(\d+.\d+)$"
URL_PATTERN = r"^http://[\w\.]+:\d+/{path}/?\??{qs}$"
REQUEST_TO_TYPE = {
    (URL_PATTERN.format(path="account/\d+", qs=""), "GET"): "retrieve_account",
    (URL_PATTERN.format(path="account", qs=""), "POST"): "create_account",
    (URL_PATTERN.format(path="account/\d+", qs=""), "PUT"): "update_account",
    (URL_PATTERN.format(path="follow", qs="followee_id=\d+"), "GET"): "retrieve_account_followers",
    (URL_PATTERN.format(path="follow", qs="follower_id=\d+"), "GET"): "retrieve_account_followees",
    (URL_PATTERN.format(path="follow", qs=""), "POST"): "follow_account",
    (URL_PATTERN.format(path="follow/\d+", qs=""), "DELETE"): "delete_follow",
    (URL_PATTERN.format(path="like", qs="account_id=\d+"), "GET"): "retrieve_account_likes",
    (URL_PATTERN.format(path="like", qs="post_id=\d+"), "GET"): "retrieve_post_likes",
    (URL_PATTERN.format(path="like", qs=""), "POST"): "like_post",
    (URL_PATTERN.format(path="like/\d+", qs=""), "DELETE"): "delete_like",
    (URL_PATTERN.format(path="post", qs=""), "GET"): "retrieve_recent_posts",
    (URL_PATTERN.format(path="post", qs="author_id=\d+"), "GET"): "retrieve_account_posts",
    (URL_PATTERN.format(path="post/\d+", qs=""), "GET"): "retrieve_post",
    (URL_PATTERN.format(path="post", qs=""), "POST"): "create_post",
    (URL_PATTERN.format(path="post/\d+", qs=""), "DELETE"): "delete_post"
}


class LoadgenParser(BaseParser):
    def __init__(self, logfile):
        super().__init__(logfile)

    def parse(self):
        data = {"timestamp": [], "method": [], "url": [], "request_id": [], "status_code": [], "latency": [],
                "status": [], "type": [], "rw": []}
        for log in self._logfile:
            timestamp, method, url, status_code, latency = re.match(REQUEST_LOG_PATTERN, log.decode("utf-8")).groups()
            request_id = re.findall(r"request_id=([a-zA-Z0-9]+)&?", url)
            url = re.sub("limit=\d+&?", "", url)
            url = re.sub("offset=\d+&?", "", url)
            url = re.sub("request_id=[a-zA-Z0-9]+&?", "", url)
            url = re.sub("&$", "", url)
            url = re.sub("\?$", "", url)
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
            data["timestamp"].append(timestamp)
            data["method"].append(method)
            data["url"].append(url)
            data["request_id"].append(request_id[0] if request_id else "")
            data["status_code"].append(int(status_code))
            data["latency"].append(float(latency))
            data["status"].append("successful" if int(status_code) == 200 else "failed")
            data["type"].append([t for ((p, m), t) in REQUEST_TO_TYPE.items() if m == method and re.match(p, url)][0])
            data["rw"].append("read" if method.upper() == "GET" else "write")
        return data