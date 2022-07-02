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
        experimentdir = f'experiment/{self.name}'
        dir = os.system(f'wsl sh -c "mkdir -p /mnt/c/Users/{user}/{experimentdir}"')
        print(dir)
        # command = f'wsl mkdir -p {self.directory}'
        # print(command)
        state = Shell.mkdir(self.directory)

        print(state)

    def run(self):
        self.mkdir_local()
        # command = f'chmod ug+x ./{self.name}.sh'
        # os.system(command)

        experimentdir = f'experiment/{self.name}'
        command = f'wsl nohup sh -c'\
                  f' ". ~/.profile && cd /mnt/c/Users/{self.username}/{experimentdir}'\
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
            except:
                return 0
        return 0

    def get_error(self):

        experimentdir = f'/mnt/c/Users/{self.username}/experiment/{self.name}'

        command = f'wsl sh -c ". ~/.profile && cp {experimentdir}/{self.name}.err ' \
                  f'./{self.name}.err"'
        print(command)
        os.system(command)
        content = readfile(f"{self.directory}/{self.name}.err", 'r')
        print(content)
        return content

    def get_log(self):

        experimentdir = f'/mnt/c/Users/{self.username}/experiment/{self.name}'

        command = f'wsl sh -c ". ~/.profile && cp {experimentdir}/{self.name}.log ' \
                  f'.{self.name}.log"'
        print(command)
        os.system(command)
        content = readfile(f"{self.directory}/{self.name}.log", 'r')
        print(content)
        return content

    # move from current directory to remote
    def sync(self):
        self.mkdir_local()

        experimentdir = f'/mnt/c/Users/{self.username}/experiment/{self.name}'
        command = f'wsl sh -c ". ~/.profile && cp {self.name}.sh {experimentdir}/{self.name}.sh"'
        print(command)
        r = os.system(command)
        return r

    def exists(self, filename):
        # command = f"{self.directory}/{filename}"
        experimentdir = f'/c/Users/{self.username}/experiment/{self.name}/{filename}'
        # print(command)
        # print("EXISTS COMMAND:", command)
        r = None
        try:
            r = Shell.run(f'ls {experimentdir}')
        except Exception as e:
            print(e.output)
        # r = Shell.ls(experimentdir)
        if r:
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

# j = Job(name='run-wsl')
# try:
#     j.get_log()
# except Exception as e:
#     print(e.output)
