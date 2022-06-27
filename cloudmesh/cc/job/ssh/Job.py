from cloudmesh.cc.job.AbstractJob import AbstractJob
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
from cloudmesh.common.Shell import Shell


class Job(AbstractJob):

    # def __init__(self, command):
    #
    #     self.command = command
    #     self.status = 'ready'

    def set_name(self, name):
        self.name = name

    def probe(self):
        self.get_status()

    def run(self):
        r = Shell.sh("test.sh","atl9rn")
        return r

    def get_status(self):
        pass

    def get_error(self):
        return readfile('{self.name}.error', 'r')

    def get_log(self):
        return readfile('{self.name}.log', 'r')


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

dict1 = {"username":"atl9rn","age":100}
# j = Job("username"="atl9rn",age=100)
j = Job()
j.run()
