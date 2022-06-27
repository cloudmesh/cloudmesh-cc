from cloudmesh.cc.job.AbstractJob import AbstractJob
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
from cloudmesh.common.Shell import Shell


class Job(AbstractJob):

    def probe(self):
        pass

    def run(self):
        Shell.sh("./test.sh", self['username'])

    def get_status(self):
        pass

    def get_error(self):
        return readfile('run.error', 'r')

    def get_log(self):
        return readfile('run.log', 'r')


    def get_progress(self):
        prog = TextFinder.find("progress=", self.get_log())
        return prog

    def sync(self):

        pass

    @property
    def status(self):

        return self.get_status()


    def watch(self, period=10):
        pass