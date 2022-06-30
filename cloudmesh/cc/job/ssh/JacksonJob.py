import os

# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
import time

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.variables import Variables


class Job():

    def __init__(self, name=None, username=None, host=None, label=None, **argv):
        """
        cms set username=abc123
        cms set host= rivanna.hpc.virginia.edu

        craetes a job by passing either a dict with **dict or named arguments
        attribute1 = value1, ...

        :param data:
        :type data:
        :return:
        :rtype:
        """

        self.data = argv

        print(self.data)
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
            self.directory = self.data["directory"]
        else:
            self.directory = f"experiment/{self.name}"

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
    # def status(self):
    #     return self.get_status()

    def mkdir_remote(self):
        enter = f'ssh {self.username}@{self.host}.hpc.virginia.edu && mkdir -p {self.directory}'
        print(enter)
        os.system(command=f'{enter}, &')
        print("DONE")


    def run(self):
        self.mkdir_remote()

        command = f'chmod ug+x ./{self.name}.sh'
        os.system(command)
        command = f'ssh {self.username}@{self.host} "cd {self.directory} && nohup ./{self.name}.sh > {self.name}.log 2> {self.name}.error && echo $pid"'
        print(command)
        state = os.system(f'{command} &')
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
            try:
                progress = lines[-1].split("progress=")[1]
                progress = progress.split()[0]
                return int(progress)
            except:
                return 0
        return 0

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
        do_sync = f"scp ./{self.name}.sh {self.username}@{self.host}:{self.directory}/."
        print(do_sync)
        r = os.system(do_sync)
        do_copy = f'cp {filepath} {self.directory}/.'
        print(do_copy)
        y = os.system(do_copy)
        return r

    def exists(self, filename):
        command = f'ssh {self.username}@{self.host} "ls {self.directory}/{filename}"'
        print(command)
        r = Shell.run(command)
        if "No such file or directory" in r:
            return False
        return True

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
        try:
            """get the pid from the job"""
            if refresh:
                log = self.get_log()
            log = readfile(f"{self.name}.log", 'r')
            lines = Shell.find_lines_with(log, "# cloudmesh")
            if len(lines) > 0:
                pid = lines[0].split("pid=")[1]
                pid = pid.split()[0]
                return pid
        except:
            pass
        return None

    def kill(self, period=1):
        """
        kills the job
        """
        found = False
        while not found:
            log = self.get_log()
            if 'pid=' in log:
                found = True
            else:
                print(f"check for {self.name}.log")
                time.sleep(period)

        pid = self.get_pid()
        command = f'pgrep -P {pid}'
        child = Shell.run(command).strip()
        command = f'kill -9 {pid} {child}'
        r = Shell.run(command)
        print(r)
        if "No such process" in r:
            Console.warning(
                "Process {pid} not found. It is likely it already completed.")
