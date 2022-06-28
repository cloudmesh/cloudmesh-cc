import os

# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.variables import Variables


class Job():

    def __init__(self, name=None, username=None, host=None, label=None, **argv):
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

        print (self.data)
        variables = Variables()
        # try:
        #    a,b,c, = self.name, self.username, self.host
        # except:
        #    Console.error("name, username, or host not set")
        #    raise ValueError


        variables = Variables()

        self.username = username
        self.host = host
        self.name = name
        if label is None:
            label = name

        print("self.data", self.data)
        for key, value in self.data.items():
            setattr(self, key, value)


        if self.name is None:
            Console.error("Name is not defined")
            raise ValueError

        if self.username is None:
            try:
                self.username = variables["username"]
            except:
                Console.error("Username is not defined")
                raise ValueError

        if self.host is None:
            try:
                self.host = variables["host"]
            except:
                Console.error("Username is not defined")
                raise ValueError

        if "directory" in self.data:
            self.directory = self.data["directry"]
        else:
            self.directory = f"~/experiment/{self.name}"

        print (self)

    def __str__(self):
        msg = []
        msg.append(f"host: {self.host}")
        msg.append(f"username: {self.username}")
        msg.append(f"name: {self.name}")
        msg.append(f"directory: {self.directory}")
        msg.append(f"data: {self.data}")
        msg.append(f"locals  {locals()}")
        return "\n".join(msg)

    @property
    def status(self):
        return self.get_status()

    def mkdir_remote(self):
        command = f'ssh {self.username}@{self.host} "mkdir -p {self.directory}"'
        print (command)
        os.system(command)

    def run(self):
        self.mkdir_remote()

        command = f'chmod ug+x ./{self.name}.sh'
        os.system(command)
        command = f'ssh {self.username}@{self.host} "cd {self.directory} && nohup ./{self.name}.sh > {self.name}.log 2> {self.name}.error; echo $pid"'
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
        command = f"scp {self.username}@{self.host}:{self.directory}/{self.name}.error {self.name}.error"
        print(command)
        os.system(command)
        content = readfile(f"{self.name}.error", 'r')
        return content

    def get_log(self):
        # scp "$username"@rivanna.hpc.virginia.edu:run.log run.log
        command = f"scp {self.username}@{self.host}:{self.directory}/{self.name}.log {self.name}.log"
        print(command)
        os.system(command)
        content = readfile(f"{self.name}.log", 'r')
        return content

    def sync(self, filepath):
        self.mkdir_remote()
        command = f"scp ./{self.name}.sh {self.username}@{self.host}:{self.directory}/."
        print(command)
        r = os.system(command)
        return r

    def exists(self, filename):
        command = f'ssh {self.username}@{self.host} "ls {self.directory}/{filename}"'
        print(command)
        r = Shell.run(command)
        if "cannot acces" in r:
            return False
        return True

    def watch(self, period=10):
        """waits and wathes every seconds in period, till the job has completed"""
        raise NotImplementedError
        pass

    def get_pid(self):
        """get the pid from the job"""
        raise NotImplementedError
        pid = 0
        return pid

    def kill(self):
        """
        kills the job
        """
        raise NotImplementedError