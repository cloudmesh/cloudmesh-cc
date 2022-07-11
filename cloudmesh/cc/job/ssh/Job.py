import os

# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
import time
import subprocess

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import path_expand
from cloudmesh.common.systeminfo import os_is_windows


class Job():

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
        self.label = label

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
        command = f'ssh {self.username}@{self.host} "mkdir -p {self.directory}"'
        print(command)
        os.system(command)

    def run(self):
        self.mkdir_experimentdir()

        command = f'chmod ug+x ./{self.name}.sh'
        os.system(command)
        if os_is_windows():

            command = f'ssh {self.username}@{self.host} "cd {self.directory} ; nohup ./{self.name}.sh > {self.name}.log 2> {self.name}.error &"'
            print(command)
            state = os.system(command)
            # ps = subprocess.Popen(('bash', '-c', f'"{command} ; exit 0" &'), stdout=subprocess.PIPE)
            # print(ps)
            # print(type(ps))
            # output = subprocess.check_output(stdin=ps.stdout)
            # ps.wait()
            # state = subprocess.check_output(['bash', '-c', f'"{command} ; exit 0" &'])
            #state = state.decode('utf-8')
            #if state == '':
            #    state = 0

        else:
            command = f'ssh {self.username}@{self.host} "cd {self.directory} && nohup ./{self.name}.sh > {self.name}.log 2> {self.name}.error"'
            # time.sleep(1)
            print(command)
            state = os.system(f'{command} &')
        sate = 0
        error = self.get_error()
        log = self.get_log()
        return state, log, error

    def clear(self):
        content = None
        try:
            source = f'~/experiment/{self.name}/{self.name}.log'
            destination = f"{self.name}.log"
            Shell.run(f"rm -f {destination}")
            Shell.run(f'ssh {self.username}@{self.host} "rm -f {source}"')
        except Exception as e:
            Console.error(e, traceflag=True)

    def get_status(self, refresh=False):
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"{self.name}.log")
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            status = lines[-1].split("status=")[1]
            status = status.split()[0]
            return status

    def get_progress(self, refresh=False):
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"{self.name}.log")
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            try:
                progress = lines[-1].split("progress=")[1]
                progress = progress.split()[0]
                return int(progress)
            except:   # noqa: E722
                return 0
        return 0

    def get_error(self):
        command = f"scp {self.username}@{self.host}:{self.directory}/{self.name}.error {self.name}.error"
        print(command)
        os.system(command)
        content = readfile(f"{self.name}.error")
        return content

    def get_log(self):
        command = f"scp {self.username}@{self.host}:{self.directory}/{self.name}.log {self.name}.log"
        print(command)
        os.system(command)
        content = readfile(f"{self.name}.log")
        return content

    def sync(self):
        self.mkdir_experimentdir()
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

        command = f'ssh {self.username}@{self.host} "pgrep -P {pid}"'
        child = Shell.run(command).strip()
        command = f'ssh {self.username}@{self.host} "kill -9 {pid} {child}"'
        print(command)
        r = Shell.run(command)
        Console.msg(f"Killing {pid} {child}")
        # log back into rivanna and repeatedly issue the ps -aux command applied to the pid and child
        # to see if these processes still exist. If they exist, they need to be killed
        # ssh rivanna ps -q 372
        #
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
