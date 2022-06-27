from cloudmesh.cc.job.AbstractJob import AbstractJob
# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES

class Job(AbstractJob):

    def get_log(self):
        return


    def get_progress(self):
        prog = TextFinder.find("progress=")
        return prog