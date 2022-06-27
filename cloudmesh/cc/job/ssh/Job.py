from cloudmesh.cc.job.AbstractJob import AbstractJob
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
from cloudmesh.common.Shell import Shell



class Job(AbstractJob):
    def __init__(self, command, status):

        self.command = command
        self.status = status

    def probe(self):
        self.get_status()

    def run(self):
        Shell.sh("./test.sh atl9rn")

    def get_status(self):
        pass

    def get_error(self):

        pass

    def get_log(self):
        return readfile('run.log', 'r')

    def get_error(self):
        pass


    def get_progress(self):
        prog = TextFinder.find("progress=", self.get_log())
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
        pass


j = Job()
j.run()
