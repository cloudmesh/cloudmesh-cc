from cloudmesh.cc.job.AbstractJob import AbstractJob
# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
from cloudmesh.common.Shell import Shell



class Job(AbstractJob):

    def run(self):
        Shell.sh("./run.sh atl9rn")

    def get_log(self):
        return True


    def get_progress(self):
        prog = TextFinder.find("progress=")
        return prog


j = Job()
print(j.run())