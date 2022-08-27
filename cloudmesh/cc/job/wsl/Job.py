import os
from pathlib import Path

import time

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile


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
        self.label = label
        self.script = None

        # print("self.data", self.data)
        for key, value in self.data.items():
            setattr(self, key, value)

        if self.script is None:
            self.filetype = 'os'
        elif '.ipynb' in self.script:
            self.filetype = 'ipynb'
        elif '.sh' in self.script:
            self.filetype = 'sh'
        elif '.py' in self.script:
            self.filetype = 'python'
        else:
            self.filetype = 'os'

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
        """
        returns pertinent information of job in string format,
        including host, username, name of job, and other characteristics
        :return: description and specifications of job in string format
        :rtype: str
        """
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
        """
        exactly the same as get_status but duplicated to provide as
        a shortened-named, alternative call
        :return: the status of job
        :rtype: str
        """
        return self.get_status()

    def mkdir_experimentdir(self):
        """
        creates experiment directory to contain job files such as
        yaml file, log file, and pertinent script to be run
        like sh script or ipynb or py
        :return: does not return anything
        :rtype: None
        """
        try:
            experimentdir = f"~/experiment/{self.name}"
            Shell.mkdir(experimentdir)
        except Exception as e:
            Console.error(str(e), traceflag=True)

    # move from current directory to remote
    def sync(self):
        """
        changes permissions and makes experiment dir, and then
        copies the shell script to experiment dir
        :return: True or False depending on if file exists
        :rtype: bool
        """
        print(self)
        self.chmod()
        self.mkdir_experimentdir()
        home = Path.home()
        cwd = Path.cwd()
        experimentdir = f"{home}/experiment/{self.name}"
        destination = Path(f"{experimentdir}/{self.name}.sh")
        source = Path(f"{cwd}/{self.name}.sh")
        Shell.copy(source, destination)
        return self.exists(f"{self.name}.sh")

    def chmod(self):
        """
        changes the permissions and flags of the script to be
        run (shell or py file, ipynb not yet supported) so that
        the system can successfully execute the script
        :return: 0 or 1 depending on success of command
        :rtype: int
        """
        cwd = Path.cwd()
        source = Path(f"{cwd}/{self.name}")
        if self.filetype == "python":
            command = f"chmod ug+rx {source}.py"
        else:
            command = f"chmod ug+rx {source}.sh"
        print(command)
        r = os.system(command)
        return r

    def exists(self, filename):
        """
        used to check if the file is existing within the experiment
        directory
        :param filename: the name of the script, including file extension
        :type filename: str
        :return: True if the file exists and False if it doesnt
        :rtype: bool
        """
        home = Path.home()
        path = f'{home}/experiment/{self.name}/{filename}'
        return Path.exists(Path(path))

    def run(self):
        """
        runs the job by making script executable and running the
        script within wsl. only works for shell scripts, as .sh is
        hardcoded within the commands
        :returns:
            - state - undefined, running, or done
            - log - the output of the job
        """
        self.mkdir_experimentdir()
        # make sure executable is set
        command = f'chmod a+x {self.name}.sh'
        os.system(command)

        home = Path.as_posix(Path.home())
        cwd = Path.as_posix(Path.cwd())
        userdir_name = os.path.split(home)[1]

        experimentdir = f'/c/Users/{userdir_name}/experiment/{self.name}'
        wsl_experimentdir = f"/mnt/c/Users/{userdir_name}/experiment/{self.name}"

        # command = f'wsl nohup sh -c' \
        #           f' ". ~/.profile && cd {wsl_experimentdir}' \
        #           f' && ./{self.name}.sh > {self.name}.log 2>&1 &"'

        Shell.mkdir(experimentdir)

        command = f'wsl nohup sh -c' \
                  f' ". ~/.profile && cd {wsl_experimentdir}' \
                  f' && ./{self.name}.sh > {self.name}.log 2>&1 &"'

        command = f'wsl nohup sh -c' \
                  f' ". ~/.profile && cd {wsl_experimentdir}' \
                  f' && /usr/bin/bash {self.name}.sh > {self.name}.log 2>&1 &"'

        # command = f'wsl --cd  {experimentdir} nohup sh -c "./{self.name}.sh > ./{self.name}.log 2>&1 &" >&/dev/null'
        # command = f'wsl --cd  {experimentdir} nohup sh -c "./{self.name}.sh > ./{self.name}.log 2>&1 &"'
        # command = f'wsl --cd  {experimentdir} nohup sh -c "./{self.name}.sh > ./{self.name}.log 2>&1 &"'

        print(command)
        state = os.system(command)

        log = self.get_log()
        # error = self.get_error()
        # error = 0
        return state, log

    def clear(self):
        """
        clears all leftover log files from past runs
        :return: does not return anything
        :rtype: None
        """
        content = None
        try:
            source = path_expand(f'~/experiment/{self.name}/{self.name}.log')
            destination = f"{self.name}.log"
            Shell.run(f"rm -f {source} {destination}")
        except Exception as e:
            Console.error(e, traceflag=True)

    def get_log(self, verbose=False):
        """
        copy the log file and read the contents of the file to
        return the contents as a string
        :param verbose: if True then print contents of log
        :type verbose: bool
        :return: the contents of the log file in string format
        :rtype: str
        """
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
        """
        fetches the log file of the job and returns the status of
        the job, which can be undefined, running, or done
        :param refresh: whether to copy the log file in case of changes
        :type refresh: bool
        :return: returns status, which is the progress of the job
        :rtype: str
        """
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
        """
        fetches the log file of the job and reads the log file to check
        for the current completeness of the job
        :param refresh: whether to copy the log file in case of changes
        :type refresh: bool
        :return: value from 0 to 100 which reflects completeness of job
        :rtype: int
        """
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

    def watch(self, period=2):
        """
        waits and watches for progress to reach 100, on interval basis
        specified in the period in seconds,
        till the job has completed
        :param period: time in seconds to check, as an interval
        :type period: float
        :return: does not return anything
        :rtype: None
        """
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
        """
        get the pid that the job is running within
        :param refresh: whether to retrieve the latest log
        :type refresh: bool
        :return: the pid (process identifier)
        :rtype: str
        """
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
        :param period: interval to use for waiting for log/pid
        :type period: float
        :returns:
            - pid - process id of the script
            - child - child of the script
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
            time.sleep(period)
        pid = None
        while pid is None:
            time.sleep(period)

            pid = self.get_pid(refresh=True)

        command = f'wsl pgrep -P {pid}'
        child = Shell.run(command).strip()
        command = f'wsl kill -9 {pid} {child}'
        r = Shell.run(command)
        Console.msg(f"Killing {pid} {child}")
        if "No such process" in r:
            Console.warning(
                f"Process {pid} not found. It is likely it already completed.")
        return pid, child
