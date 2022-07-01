import os

import time

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

        print(self.data)
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
            self.directory = self.data["directory"]
        else:
            # if os_is_windows():
            #     self.directory = f"~\\experiment\\{self.name}"
            # else:
            #     self.directory = f"~/experiment/{self.name}"

            from cloudmesh.common.util import path_expand
            # self.directory = path_expand(f"~/experiment/{self.name}")
            self.directory = f"\\\\wsl$\\Ubuntu\\home\\{self.username}"


        print(self)

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

    def mkdir(self):
        command = f'wsl mkdir -p {self.directory}'
        print(command)
        Shell.mkdir(self.directory)

    def run(self):
        # self.mkdir()

        command = f'wsl chmod ug+x ./{self.name}.sh'
        os.system(command)
        # command = f'ssh {self.username}@{self.host} "cd {self.directory} && nohup ./{self.name}.sh > {self.name}.log 2> {self.name}.error; echo $pid"'
        # command = f'cd {self.directory} && start /min {self.name} > {self.name}.log'

        # from pathlib import Path
        # path = Path(self.directory)
        # print(f'cd {self.directory}')

        # os.chdir(str(path))
        print(Shell.run("pwd"))
        # os.chdir(self.directory)

        # command = f'nohup bash {self.name}.sh > {self.name}-log.txt 2>{self.name}-error.txt'
        bash = "C:\\Program Files\\Git\\usr\\bin\\bash.exe"
        command = f'wsl bash {self.name}.sh > {self.name}-log.txt 2>{self.name}-error.txt'
        print(command)
        state = os.system(command)

        error = self.get_error()
        log = self.get_log()
        return state, log, error

    def get_status(self, refresh=False):
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"{self.name}-log.txt", 'r')
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            status = lines[-1].split("status=")[1]
            status = status.split()[0]
            return status

    def get_progress(self, refresh=False):
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"{self.name}-log.txt", 'r')
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            try:
                progress = lines[-1].split("progress=")[1]
                progress = progress.split()[0]
                return int(progress)
            except:
                return 0
        return 0

    def get_error(self):
        # scp "$username"@rivanna.hpc.virginia.edu:run.error run.error
        # command = f"scp {self.username}@{self.host}:{self.directory}/{self.name}.error {self.name}.error"
        # print(command)
        # os.system(command)
        content = readfile(f"{self.name}-error.txt", 'r')
        return content

    def get_log(self):
        # scp "$username"@rivanna.hpc.virginia.edu:run.log run.log
        # command = f"scp {self.username}@{self.host}:{self.directory}/{self.name}.log {self.name}.log"
        # print(command)
        # os.system(command)
        content = readfile(f"{self.name}-log.txt", 'r')
        return content


    # def sync(self, filepath):
    #     self.mkdir()
    #     command = f"scp ./{self.name}.sh {self.username}@{self.host}:{self.directory}/."
    #     print(command)
    #     r = os.system(command)
    #     return r


    def sync(self, filename=None):
        if filename is None:
            filename = f"{self.name}.sh"
        self.mkdir()
        # command = f'cp {filename} {self.directory}/.'
        print(self.name)
        command = f'cp {filename} {self.directory}\\{filename}'
        print(command)
        r = os.system(command)
        return r

    def exists(self, filename):
        # command = f'wsl ls {self.directory}/{filename}'
        command = f'{self.directory}\\{filename}'
        # print(command)
        r = Shell.ls(command)
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", r)
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAbbbbbbbbb", len(r))
        if len(r) > 0:
            return True
        return False

    def watch(self, period=10):
        """waits and wathes every seconds in period, till the job has completed"""
        finished = False
        while not finished:
            progress = int(self.get_progress(refresh=True))
            finished = progress == 100
            if not finished:
                time.sleep(period)

    def get_pid(self, refresh=False):
        """get the pid from the job"""
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"{self.name}-log.txt", 'r')
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            pid = lines[0].split("pid=")[1]
            pid = pid.split()[0]
            return pid
        return None


class a:
    def kill(self):
        """
        kills the job
        """
        pid = self.get_pid()
        command = ""
        command = f'kill -9 {pid}'
        print(command)
        r = Shell.run(command)
        print(r)
        if "No such process" in r:
            Console.warning(
                "Process {pid} not found. It is likely it already completed.")
