import os

# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
import time

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables
from pathlib import Path


class Job():

    def __init__(self, name=None, username=None, host=None, label=None, **argv):
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

        variables = Variables()

        self.username = username
        self.host = host
        self.name = name
        if label is None:
            label = name

        # print("self.data", self.data)
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
                Console.error("Host is not defined")
                raise ValueError


        if "directory" in self.data:
            self.directory = self.data["directory"]
        else:
            self.directory = f'~/experiment/{self.name}'

        # print(self)

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

    def reset_local_dir(self):
        user = os.environ["USERNAME"]
        homedir = f'/mnt/c/Users/{user}'
        Shell.run(f'wsl sh -c ". ~/.profile && cd {homedir}"')

    def mkdir_local(self):
        self.reset_local_dir()
        user = os.environ["USERNAME"]
        bashdir = str(f'{self.directory}')[2:]
        dir = Shell.run(f'wsl sh -c "cd /mnt/c/Users/{user}/{bashdir} '
                        f'&& pwd"')
        print(dir)
        command = f'wsl mkdir -p {self.directory}'
        print(command)
        state = os.system(command)
        print(state)
        # Shell.run(f'wsl sh -c ". ~/.profile && cd')
        # Shell.mkdir(f'{self.directory}')


    def run(self):
        self.mkdir_local()
        # command = f'chmod ug+x ./{self.name}.sh'
        # os.system(command)


        state = Shell.run(f'wsl nohup sh -c ". ~/.profile && cd'
                          f' /mnt/c/Users/{self.username}/{self.directory} && ./run.sh &"')
        # state = os.system(command)
        # r = Shell.run(command)
        # print (r)
        # print(state)
        # log = self.get_log()
        return state

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
            except:
                return 0
        return 0

    # def get_error(self):
    #     command = f"scp{self.directory}/{self.name}.error {self.name}.error"
    #     print(command)
    #     os.system(command)
    #     content = readfile(f"{self.name}.error", 'r')
    #     return content

    def get_log(self):
        # print(dir)
        # bashdirectory = str(f'{self.directory}')[2:]
        # localpath = str(Path.home()) + '\\' + bashdirectory
        # localpath1 = ''
        # command = f"cp {self.directory}{self.name}.log"
        # os.system(command)
        # print(f"{localpath}\\\\{self.name}.log")
        # print({self.directory})
        state = Shell.run(f'wsl nohup sh -c ". ~/.profile && cd'
                          f'{self.directory}')
        content = readfile(f"{self.directory}/{self.name}.log", 'r')
        # print(f"{content}")
        return content

    def sync(self):
        self.mkdir_local()
        log = f'wsl sh -c ". ~/.profile && cp /mnt/c/Users/' \
                f'{self.username}/{self.directory}/{self.name}.log ' \
                f'{self.directory}/{self.name}.log'
        print(log)
        r = os.system(log)
        error = f'wsl sh -c ". ~/.profile && cp /mnt/c/Users/' \
                f'{self.username}/{self.directory}/{self.name}.err ' \
                f'{self.directory}/{self.name}.err'
        print(error)
        e = os.system(error)
        return r

    def exists(self, filename):
        command = f"{self.directory}/{filename}"
        #        print(command)
        r = Shell.ls(command)
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


j = Job(name='beige')
j.reset_local_dir()



