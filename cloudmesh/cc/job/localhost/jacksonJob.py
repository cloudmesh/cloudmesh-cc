import os

import time

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import path_expand


class Job():

    def __init__(self, name=None, username=None, host=None, label=None, test_directory=None, output_directory=None, directory=None, **argv):
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
        self.test_directory = test_directory
        output_directory = output_directory
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
            self.directory = f'~/experiment/{self.name}'

        if self.test_directory is None:
            self.test_directory = '~/cm/cloudmesh-cc/tests/workflow-sh'

        if output_directory is None:
            self.output_directory = '~/cm/cloudmesh-cc/tests/test-output'

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

    def mkdir_local(self):
        command = f'mkdir -p {self.directory}'
        os.system(command)

    @property
    def status(self):
        return self.get_status()

    def mkdir_experimentdir(self):
        command = f'mkdir -p {self.directory}'
        print(command)
        os.system(command)

    def run(self):
        if not os.path.isdir(self.directory):
            self.mkdir_experimentdir()

        command = f'cd {self.directory} && chmod ug+x ./{self.name}.sh'
        os.system(command)
        command = f'cd {self.directory} && nohup ./{self.name}.sh > {self.output_directory}/{self.name}.log 2> {self.output_directory}/{self.name}.error'
        print(command)
        state = os.system(f'{command} &')
        logfile = path_expand(f"{self.directory}/{self.name}.sh")
        errorfile = path_expand(f"{self.directory}/{self.name}.sh")

        started = False
        while started:
            os.system("sync")
            started = os.path.exists(logfile) and os.path.exists(errorfile)
            print("STARTED")
            if not started:
                time.sleep(0.1)
        error = self.get_error()
        log = self.get_log()
        return state, log, error

    def clear(self):
        content = None
        try:
            source = f'~/experiment/{self.name}/{self.name}.log'
            destination = f"{self.name}.log"
            Shell.run(f"rm -f {destination}")
            Shell.run(f"rm -f {source}")
        except Exception as e:
            Console.error(e, traceflag=True)

    def get_status(self, refresh=False):
        status = "undefined"
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"{self.directory}/{self.name}.log")
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            status = lines[-1].split("status=")[1]
            status = status.split()[0]
        return status

    def get_progress(self, refresh=False):
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"{self.directory}/{self.name}.log")
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
        command = f"cp {self.directory}/{self.name}.error {self.name}.error"
        print(command)
        os.system(command)
        os.system("sync")
        content = readfile(f"{self.output_directory}/{self.name}.error")
        return content

    def get_log(self):
        content = None
        try:
            command = f"cp {self.directory}/{self.name}.log {self.output_directory}/{self.name}.log"
            print(command)
            os.system(command)
            os.system("sync")
            content = readfile(f"{self.name}.log")
        except:
            pass
        return content

    def sync(self):
        self.mkdir_experimentdir()
        command = f"cd {self.test_directory} && cp {self.name}.sh {self.directory}/."
        print(command)
        os.system("sync")
        r = os.system(command)
        return r

    def exists(self, filename):
        return os.path.exists(path_expand(f'{self.directory}/{filename}'))

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
            log = readfile(f"{self.name}.log")
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            pid = lines[0].split("pid=")[1]
            pid = pid.split()[0]
            return pid
        return None

    def kill(self, period=1):
        """
        kills the job
        """
        #
        # find logfile
        #

        logfile = f'{self.name}.log'
        log = None
        while log is None:
            try:
                self.get_log()
                log = readfile(logfile)
                lines = log.splitlines()
                found = False
                for line in lines:
                    if line.startswith("# cloudmesh") and "pid=" in line:
                        found = True
                        break
                if not found:
                    log = None
            except Exception as e:
                Console.error("no log file yet", traceflag=True)
                log = None
            time.sleep(2)
        pid = None
        while pid is None:
            time.sleep(1)
            pid = self.get_pid(refresh=True)

        command = f'pgrep -P {pid}'
        child = Shell.run(command).strip()
        command = f'kill -9 {pid} {child}'
        print(command)
        r = Shell.run(command)
        Console.msg(f"Killing {pid} {child}")
        print(r)
        if "No such process" in r:
            Console.warning(
                f"Process {pid} not found. It is likely it already completed.")
        return pid, child

    def create(self, command, ntasks=1):
        """
        creates a template
        for the slurm sbatch
        """
        template = \
            f"""
        #!/bin/bash
        #
        #SBATCH --job-name=test
        #SBATCH --output=result.out
        #
        #SBATCH --ntasks={ntasks}
        #
        """
        template += f"\n{command}"