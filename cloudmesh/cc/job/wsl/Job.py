import os

import time
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import path_expand
from pathlib import Path

class Job:

    def __init__(self, name=None, username=None, host=None, label=None, directory=None, **argv):
        """
        cms set username=abc123

        creates a job by passing either a dict with **dict or named arguments
        attribute1 = value1, ...

        :param data:
        :type data:
        :return:
        :rtype:
        """

        self.data = argv

        self.username = username
        self.host = host
        self.name = name
        self.directory = directory
        if label is None:
            self.label = name

        # print("self.data", self.data)
        for key, value in self.data.items():
            setattr(self, key, value)

        if self.name is None:
            Console.error("Name is not defined")
            raise ValueError

        if self.username is None:
            self.username = os.environ["USERNAME"]

        if self.host is None:
            self.host = "localhost"

        if self.directory is None:
            self.directory = f'/c/Users/{self.username}/experiment/{self.name}'

    def __str__(self):
        msg = [
            f"host:      {self.host}",
            f"username:  {self.username}",
            f"name:      {self.name}",
            f"label:     {self.label}",
            f"directory: {self.directory}",
            f"data:      {self.data}",
            f"locals     {locals()}"
        ]
        return "\n".join(msg)

    @property
    def status(self):
        return self.get_status()

    def mkdir_experimentdir(self):
        try:
            experimentdir = f"~/experiment/{self.name}"
            Shell.mkdir(experimentdir)
        except Exception as e:
            Console.error(str(e))

    # move from current directory to remote
    def sync(self):
        print (self)
        self.mkdir_experimentdir()
        home = Path.home()
        cwd = Path.cwd()

        print (home, cwd)

        experimentdir = f"{home}/experiment/{self.name}"
        destination = Path(f"{experimentdir}/{self.name}.sh")
        source = Path(f"{cwd}/{self.name}.sh")
        Shell.copy(source,  destination)
        print ("JJJJ", destination)
        return self.exists(f"{self.name}.sh")

    def exists(self, filename):
        home = Path.home()
        path = f'{home}/experiment/{self.name}/{filename}'
        return Path.exists(Path(path))

    def run(self):
        self.mkdir_experimentdir()
        # make sure executable is set
        command = f'chmod a+x ./{self.name}.sh'
        os.system(command)

        experimentdir = f'/c/Users/{self.username}/experiment/{self.name}'
        #command = f'wsl --cd  {experimentdir} nohup sh -c "./{self.name}.sh > ./{self.name}.log 2>&1 &" >&/dev/null'
        #command = f'wsl --cd  {experimentdir} nohup sh -c "./{self.name}.sh > ./{self.name}.log 2>&1 &" >&/dev/null'

        command = f'wsl nohup sh -c' \
                  f' ". ~/.profile && cd /mnt{experimentdir}' \
                  f' && ./{self.name}.sh > ./{self.name}.log 2>&1 &"'
        print(command)
        r = os.system(command)

        # r = Shell.run(command)
        # print (r)

        state = r
        log = self.get_log()
        # error = self.get_error()
        error = 0
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
            try:
                progress = lines[-1].split("progress=")[1]
                progress = progress.split()[0]
                return int(progress)
            except:  # noqa: E722
                return 0
        return 0

    def get_error(self):

        experimentdir = f'/mnt/c/Users/{self.username}/experiment/{self.name}'

        command = f'cp {experimentdir}/{self.name}.err ./{self.name}.err'
        print(command)
        os.system(command)
        content = readfile(f"{self.name}.err", 'r')
        print(content)
        return content

    def get_log(self):

        experimentdir = f'c/Users/{self.username}/experiment/{self.name}'

        command = f'cp {experimentdir}/{self.name}.log ./{self.name}.log'
        print(command)
        os.system(command)
        content = readfile(f"{self.name}.log", 'r')
        print(content)
        return content


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
            log = readfile(f"{self.name}.log", 'r')
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            pid = lines[0].split("pid=")[1]
            pid = pid.split()[0]
            return pid
        return None

    def kill(self):
        """
        kills the job
        """
        pid = self.get_pid()
        command = f"wsl kill -9 {pid}"
        #        print(command)
        # the kill command needs to be run in WSL
        r = Shell.run(command)
        #        print(r)
        if "No such process" in r:
            Console.warning(
                f"Process {pid} not found. It is likely it already completed.")
