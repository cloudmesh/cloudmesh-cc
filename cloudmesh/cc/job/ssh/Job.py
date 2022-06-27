import os

# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.variables import Variables


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

        self.data = argv
        print("self,data", self.data)

        variables = Variables()
        # try:
        #    a,b,c, = self.name, self.username, self.host
        # except:
        #    Console.error("name, username, or host not set")
        #    raise ValueError

        if "username" not in self.data:
            self.data["username"] = variables["username"]
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

    @property
    def status(self):
        return self.get_status()

    def run(self):
        command = f'chmod ug+x ./{self.name}.sh'
        os.system(command)
        command = f'ssh {self.username}@{self.host} "nohup sh ./{self.name}.sh > {self.name}.log 2>{self.name}.error; echo $pid"'
        print(command)
        state = os.system(command)
        error = self.get_error()
        log = self.get_log()
        return state, log, error

    def get_status(self, refresh=False):
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"{self.name}.log", 'r')
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            status = lines[-1].split("status=")[1]
            status = status.split()[0]
            return status

    def get_progress(self, refresh=False):
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"{self.name}.log", 'r')
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            status = lines[-1].split("progress=")[1]
            status = status.split()[0]
            return status

    def get_error(self):
        # scp "$username"@rivanna.hpc.virginia.edu:run.error run.error
        command = f"scp {self.username}@{self.host}:{self.name}.error {self.name}.error"
        print(command)
        os.system(command)
        content = readfile(f"{self.name}.error", 'r')
        return content

    def get_log(self):
        # scp "$username"@rivanna.hpc.virginia.edu:run.log run.log
        command = f"scp {self.username}@{self.host}:{self.name}.log {self.name}.log"
        print(command)
        os.system(command)
        content = readfile(f"{self.name}.log", 'r')
        return content

    def sync(self, filepath):
        command = f"scp ./{self.name}.sh {self.username}@{self.host}:."
        print(command)
        r = os.system(command)
        return r

    def exists(self, filename):
        return True
        # shell run ls check if file exists
        raise NotImplementedError
