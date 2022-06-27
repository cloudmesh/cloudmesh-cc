from cloudmesh.cc.job.AbstractJob import AbstractJob
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
from cloudmesh.common.Shell import Shell

from cloudmesh.cc.job.AbstractJob import AbstractJob
from cloudmesh.common.util import readfile
class Job(AbstractJob):
    def get_log(self):
        return readfile('run.log', 'r')

    def get_progress(self):
        prog = TextFinder.find("progress=", self.get_log())
        return prog
    def __init__(self):
        pass

    def probe(self):
        pass

    def run(self):
        Shell.sh("./run.sh atl9rn")

    def get_status(self):
        pass

    def get_error(self):

        pass

    def get_log(self):
        return True

    def get_progress(self):
        prog = TextFinder.find("progress=")
        return prog

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
>>>>>>> origin/main
