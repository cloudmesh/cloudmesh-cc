import os

import time
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import banner
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
            Console.error(str(e), traceflag=True)

    # move from current directory to remote
    def sync(self):
        print(self)
        self.mkdir_experimentdir()
        home = Path.home()
        cwd = Path.cwd()
        experimentdir = f"{home}/experiment/{self.name}"
        destination = Path(f"{experimentdir}/{self.name}.sh")
        source = Path(f"{cwd}/{self.name}.sh")
        Shell.copy(source, destination)
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

        home = Path.as_posix(Path.home())
        cwd = Path.as_posix(Path.cwd())
        userdir_name = os.path.split(home)[1]

        experimentdir = f'/c/Users/{userdir_name}/experiment/{self.name}'
        wsl_experimentdir = f"/mnt/c/Users/{userdir_name}/experiment/{self.name}"

        command = f'wsl nohup sh -c' \
                  f' ". ~/.profile && cd {wsl_experimentdir}' \
                  f' && ./{self.name}.sh > ./{self.name}.log 2>&1 &"'

        os.system(f'mkdir -p "{experimentdir}"')
        command = f'wsl nohup sh -c' \
                  f' ". ~/.profile && cd {wsl_experimentdir}' \
                  f' && ./{self.name}.sh > {self.name}.log 2>&1 &"'

        # command = f'wsl --cd  {experimentdir} nohup sh -c "./{self.name}.sh > ./{self.name}.log 2>&1 &" >&/dev/null'
        # command = f'wsl --cd  {experimentdir} nohup sh -c "./{self.name}.sh > ./{self.name}.log 2>&1 &"'
        # command = f'wsl --cd  {experimentdir} nohup sh -c "./{self.name}.sh > ./{self.name}.log 2>&1 &"'

        print(command)
        state = os.system(command)

        log = self.get_log()
        log = 1
        # error = self.get_error()
        error = 0
        return state, log, error

    def clear(self):
        content = None
        try:
            source = path_expand(f'~/experiment/{self.name}/{self.name}.log')
            destination = f"{self.name}.log"
            Shell.run(f"rm -f {source} {destination}")
        except Exception as e:
            Console.error(e, traceflag=True)

    def get_log(self, verbose=False):
        content = None
        try:
            logfile = f'~/experiment/{self.name}/{self.name}.log'
            source = path_expand(logfile)
            destination = f"{self.name}.log"
            if verbose:
                print("COPY", source, destination)
            Shell.copy(source, destination)
            content = readfile(destination)
            if verbose:
                print(content)
        except Exception as e:
            Console.error(e, traceflag=True)
        return content

    def get_status(self, refresh=False):
        status = "undefined"
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
            except:  # noqa: E722
                return 0
        return 0

    def get_error(self):
        experimentdir = f'/mnt/c/Users/{self.username}/experiment/{self.name}'
        command = f'cp {experimentdir}/{self.name}.err ./{self.name}.err'
        print(command)
        os.system(command)
        content = readfile(f"{self.name}.err")
        print(content)
        return content

    def watch(self, period=2):
        """waits and wathes every seconds in period, till the job has completed"""
        finished = False
        banner("watch progress")
        while not finished:
            try:
                progress = int(self.get_progress(refresh=True))
                print("Progress", progress)
                finished = progress == 100
            except:  # noqa: E722
                print("Progress", "not found")
            if not finished:
                time.sleep(period)

    def get_pid(self, refresh=False):
        """get the pid from the job"""
        pid = None
        try:
            if refresh:
                log = self.get_log()
            else:
                log = readfile(f"{self.name}.log")
            lines = Shell.find_lines_with(log, "# cloudmesh")
            if len(lines) > 0:
                pid = lines[0].split("pid=")[1]
                pid = pid.split()[0]
                return pid
        except:  # noqa: E722
            pid = None
        return pid

    def kill(self, period=1):
        """
        kills the job
        """
        #
        # find logfile
        #
        logfile = f'~/experiment/{self.name}/{self.name}.log'

        log = None
        while log is None:
            try:
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

        command = f'wsl pgrep -P {pid}'
        child = Shell.run(command).strip()
        command = f'wsl kill -9 {pid} {child}'
        r = Shell.run(command)
        Console.msg(f"Killing {pid} {child}")
        if "No such process" in r:
            Console.warning(
                "Process {pid} not found. It is likely it already completed.")
        return pid, child
