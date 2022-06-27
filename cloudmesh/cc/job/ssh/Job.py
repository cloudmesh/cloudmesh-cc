from cloudmesh.cc.job.AbstractJob import AbstractJob
from cloudmesh.common.util import readfile
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

<<<<<<< HEAD
class Job(AbstractJob):

    # def __init__(self, command):
    #
    #     self.command = command
    #     self.status = 'ready'
=======
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

        for a in argv:
            print("AAA",a)

        # super().__init__(**argv)

        print("argv", argv)

        self.data = {} #dict(argv)
        for key in argv:
            self.data[key] = argv[key]

        self.username = None
        self.host = None
        self.name = None

        print("self.data", self.data)

        variables = Variables()
        if "username" not in self.data:
            self.username=variables["username"]
        if "name" not in self.data:
            Console.error("Name not defined")
            raise ValueError
        if "host" not in self.data:
            Console.error("Host not defined")
            raise ValueError
>>>>>>> 159f09235033c20f0d1b670303277a8d7246b15b

    def set_name(self, name):
        self.name = name

    def probe(self):
        self.get_status()

    def run(self):
        # return tuple
        command = f'ssh {self.username}@{self.host} "nohup ./{self.name}.sh > {self.name}.log 2>{self.name}.error; echo $pid"'
        state = os.system(command)
        error = self.get_error()
        log = self.get_log()
        return state, log, error

    def get_status(self):
        pass

    def get_error(self):
<<<<<<< HEAD
        return readfile('{self.name}.error', 'r')

    def get_log(self):
        return readfile('{self.name}.log', 'r')

=======
        # scp "$username"@rivanna.hpc.virginia.edu:run.error run.error
        command = f"scp {self.username}@{self.host}:{self.name}.error {self.name}.error"
        os.system(command)
        return readfile(f"{self.name}.error", 'r')

    def get_log(self):
        # scp "$username"@rivanna.hpc.virginia.edu:run.log run.log
        command = f"scp {self.username}@{self.host}:{self.name}.log {self.name}.log"
        os.system(command)
        content = readfile(f"{self.name}.log", 'r')
        return content
>>>>>>> 159f09235033c20f0d1b670303277a8d7246b15b

    def get_progress(self):
        search = readfile('run.log', 'r')
        last = search.rfind(self.get_log())
        prog = readfile("progress=", last)
        return prog


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
        command = f"scp {self.name}.sh {self.username}@{self.host}:."
        os.system(command)

    @property
    def status(self):
        return self.get_status()

    def watch(self, period=10):
        pass

    def exists(self, filename):
        return True
        # shell run ls check if file exists
        raise NotImplementedError
