class BaseParser:
    def __init__(self, logfile):
        self._logfile = logfile

    def parse(self):
        raise NotImplementedError