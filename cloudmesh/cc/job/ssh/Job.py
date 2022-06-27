from cloudmesh.cc.job.AbstractJob import AbstractJob
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile

class Job(AbstractJob):

    def __init__(self):
        s

    def probe(self):
        pass

    def run(self):
        pass

    def get_status(self):
        pass

    def get_error(self):

        pass

    def get_log(self):
        pass

    def get_progress(self):
        pass

    def sync(self):

        pass

    @property
    def status(self):

        return self.get_status()

    @property
    def get(self, attribute):

        pass

    def progress(self):
        return self.get("progress")

    def watch(self, period=10):

