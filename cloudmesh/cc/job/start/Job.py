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

    def __init__(self, name=None, label=None, **argv):
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

        # print(self.data)
        # try:
        #    a,b,c, = self.name, self.host
        # except:
        #    Console.error("name, or host not set")
        #    raise ValueError

        variables = Variables()

        self.name = name
        if label is None:
            label = name

        # print("self.data", self.data)
        for key, value in self.data.items():
            setattr(self, key, value)

        if self.name is None:
            Console.error("Name is not defined")
            raise ValueError

        if "directory" in self.data:
            self.directory = self.data["directory"]
        else:
            self.directory = f"~/experiment/{self.name}"

        # print(self)

    def __str__(self):
        msg = []
        msg.append(f"name: {self.name}")
        msg.append(f"directory: {self.directory}")
        msg.append(f"data: {self.data}")
        msg.append(f"locals  {locals()}")
        return "\n".join(msg)

    @property
    def status(self):
        return self.get_status()

    def mkdir_local(self):
        # command = f"mkdir {self.directory}"
        # os.system(command)
        Shell.mkdir(f'{self.directory}')

    def run(self):
        self.mkdir_local()
        # command = f'chmod ug+x ./{self.name}.sh'
        # os.system(command)

        # command = f'cd {self.directory} && bash {self.name}.sh > ' \
        #           f'{self.name}.log 2> {self.name}.err'
        dir = path_expand('~')
        resetdir = f'cd {dir}'
        os.system(resetdir)
        bashdir = str(f'{self.directory}')[2:]
        # command = f'cd {bashdir} && wsl -e {self.name}.sh'
        username = os.environ["USERNAME"]
<<<<<<< HEAD:cloudmesh/cc/job/localhost/AlexJob.py
        print(username)
        command = f'wsl cd //mnt//c//Users///{username}//experiment//run && pwd'
=======
        command = f'wsl "cd /mnt/c/Users/{username}/experiment/run && pwd"'
        # command = f'wsl "cd /mnt/c/Users/{username}/experiment/run/run.sh &"'
>>>>>>> e6804b12bf8beadfd92b80670dc25756e3cbd372:cloudmesh/cc/job/start/Job.py
        print(command)
        state = os.system(command)
        # r = Shell.run(command)
        # print (r)
        print(state)
        log = self.get_log()
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
        dir = path_expand(f'{self.directory}')
        # print(dir)
        # bashdirectory = str(f'{self.directory}')[2:]
        # localpath = str(Path.home()) + '\\' + bashdirectory
        localpath1 = ''
        # command = f"cp {self.directory}{self.name}.log"
        # os.system(command)
        # print(f"{localpath}\\\\{self.name}.log")
        # print({self.directory})
        content = readfile(f"{self.directory}/{self.name}.log", 'r')
        # print(f"{content}")
        return content

    def sync(self, filename=None):
        if filename is None:
            filename = f"{self.name}.sh"
        self.mkdir_local()
        command = f"scp ./{filename} {self.directory}/."
        print(command)
        r = os.system(command)
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


