from cloudmesh.cc.job.AbstractJob import AbstractJob
from cloudmesh.common.util import readfile, path_expand
from cloudmesh.common.util import writefile
# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
from cloudmesh.common.Shell import Shell
from cloudmesh.common.variables import Variables
from cloudmesh.common.console import Console

import os

class Job():
    def __init__(self, **argv):
        """
        cms set username=abc123

        craetes a job by passing either a dict with **dict or named arguments
        attribute1 = value1, ...

        :param data:
        :type data:
        :return:
        :rtype:
        """

        '''
        if self.colors is None:
            self.colors = {}
        if key not in self.colors:
            self.colors[key] = {}
        self.colors[key].update(**colors)
        
        '''

        self.data = argv
        print("self,data", self.data)

        variables = Variables()
        if "username" not in self.data:
            self.data["username"]=variables["username"]
        if "name" not in self.data:
            Console.error("Name not defined")
            raise ValueError
        if "host" not in self.data:
            Console.error("Host not defined")
            raise ValueError

    @property
    def name(self):
        return self.data["name"]

    @property
    def username(self):
        return self.data["username"]

    @property
    def host(self):
        return self.data["host"]

    def probe(self):
        self.get_status()

    def run(self):
        # return tuple
        command = f'ssh {self.username}@{self.host} "nohup ./{self.name}.sh > {self.name}.log 2>{self.name}.error; echo $pid"'
        print(command)
        state = os.system(command)
        error = self.get_error()
        log = self.get_log()
        return state, log, error

    def get_status(self, refresh=False):
        if refresh:
            log = self.get_log()
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            status = lines[-1].split("status=")[1]
            status = status.split()[0]


    def get_error(self):
        # scp "$username"@rivanna.hpc.virginia.edu:run.error run.error
        command = f"scp {self.username}@{self.host}:{self.name}.error {self.name}.error"
        print(command)
        os.system(command)
        return readfile(f"{self.name}.error", 'r')

    def get_log(self):
        # scp "$username"@rivanna.hpc.virginia.edu:run.log run.log
        command = f"scp {self.username}@{self.host}:{self.name}.log {self.name}.log"
        print(command)
        os.system(command)
        content = readfile(f"{self.name}.log", 'r')
        return content

    def get_progress(self, refresh=False):
        if refresh:
            log = self.get_log()
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            status = lines[-1].split("progress=")[1]
            status = status.split()[0]
        # search = readfile('run.log', 'r')
        # last = search.rfind(self.get_log())
        # prog = readfile("progress=", last)
        # return prog


    '''
    #!/bin/bash -x
    username="$1"

    scp run.sh "$username"@rivanna.hpc.virginia.edu:.
    ssh "$username"@rivanna.hpc.virginia.edu cat run.sh
    ssh "$username"@rivanna.hpc.virginia.edu "nohup ./run.sh > run.log 2>run.error; echo $pid"
    #ssh "$username"@rivanna.hpc.virginia.edu "nohup ./run.sh > run.error; echo $pid"
    scp "$username"@rivanna.hpc.virginia.edu:run.log run.log
    scp "$username"@rivanna.hpc.virginia.edu:run.error run.error

    cat run.log
    '''
    def sync(self):
        # scp run.sh "$username"@rivanna.hpc.virginia.edu:.
        command = f"scp {path_expand(self.name)}.sh {self.username}@{self.host}:."
        print(command)
        r = os.system(command)
        return r

    @property
    def status(self):
        return self.get_status()

    def watch(self, period=10):
        pass

    def exists(self, filename):
        return True
        # shell run ls check if file exists
        raise NotImplementedError
