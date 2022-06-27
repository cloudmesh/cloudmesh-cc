
from cloudmesh.cc.job.AbstractJob import AbstractJob
from cloudmesh.common.util import readfile
class Job(AbstractJob):

    def get_log(self):
        return readfile('run.log', 'r')

    def get_progress(self):
        prog = TextFinder.find("progress=", self.get_log())
        return prog