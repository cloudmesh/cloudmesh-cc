"""Submit a job to the local host."""

import os
import subprocess
import time
import textwrap

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.systeminfo import os_is_windows


class Job:
    """
    Class to submit a job to the local host. Supported operating systems:

    * Linux
    * MacOS
    * Windows.
    """

    def __init__(self, **argv):
        """
        cms set username=abc123

        creates a job by passing either a dict with **dict or named arguments
        attribute1 = value1, ...

        :param data:
        :type data:
        :return:
        :rtype:
        """
        self.name = None
        self.username = None
        self.host = None
        self.label = None
        self.directory = None
        self.exec = None
        self.script = None

        # print("self.data", self.data)
        self.data = argv
        for key, value in self.data.items():
            setattr(self, key, value)

        if self.name is None:
            Console.error("Name is not defined", traceflag=True)

        has_extension = False
        types = ['.sh', '.py', '.ipynb']

        for file_extension in types:
            if str(self.name).endswith(file_extension):
                has_extension = True
                self.filetype = file_extension
                self.name = str(self.name).removesuffix(file_extension)

        if not has_extension:
            self.filetype = '.sh'

        self.username = self.username or Shell.user()
        self.host = self.host or "localhost"
        self.directory = self.directory or f'~/experiment/{self.name}'

        self.kind = "local"
        self.label = self.label or self.name

        if self.script is None and self.exec is not None:
            self.script = self.create_script(self.exec)

        #if self.exec is None and self.script is None:
        #    Console.warning("either exec or script must be set")

    def script_type(self, name):
        """
        Uses the inputted name of script to return the
        corresponding file extension that is run, such as
        shell script, jupyter notebook, or python file

        :param name: the name of the script
        :return: file extension of script
        :rtype: str
        """
        kind = "sh"
        if name is None:
            return kind
        for kind in ["sh", "ipynb", "sh", "py"]:
            if name.endswith(f".{kind}"):
                return kind
        return "os"


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
            f"filetype:  {self.filetype}",
            f"script:    {self.script}",
            f"exec:      {self.exec}",
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
        directory = Shell.map_filename(self.directory).path
        Shell.mkdir(directory)

    def run(self):
        """
        runs the job by making script executable and running the
        script locally. only works for shell scripts, as .sh is
        hardcoded within the commands

        :return: 0 if successfully run and 1 if failed
        :rtype: int
        """
        self.mkdir_experimentdir()

        if self.filetype == ".py":
            command = f'chmod ug+x ./runtime/{self.name}.py'
            os.system(command)
            if os_is_windows():
                state = None
                try:
                    command = fr'"%ProgramFiles%\Git\bin\bash.exe" -c "cd {self.directory} && python ./{self.name}.py > {self.name}.log 2>&1"'
                    print(command)
                    r = subprocess.Popen(command, shell=True)
                    state = 0
                except Exception as e:
                    print(e)
                    state = 1
            else:
                command = f'cd {self.directory} && python ./{self.name}.py > {self.name}.log 2>&1'
                print(command)
                state = os.system(f'{command} &')

            logfile = path_expand(f"{self.directory}/{self.name}.log")

        elif self.filetype == ".ipynb":
            command = f'chmod ug+x ./runtime/{self.name}.ipynb'
            os.system(command)
            if os_is_windows():
                state = None
                try:
                    command = fr'"%ProgramFiles%\Git\bin\bash.exe" -c "cd {self.directory} && papermill ./{self.name}.ipynb ./{self.name}-output.ipynb"'
                    print(command)
                    r = subprocess.Popen(command, shell=True)
                    state = 0
                except Exception as e:
                    print(e)
                    state = 1
            else:
                command = f'cd {self.directory} && papermill ./{self.name}.ipynb ./{self.name}-output.ipynb'
                print(command)
                state = os.system(f'{command} &')

            logfile = path_expand(f"{self.directory}/{self.name}.log")

        else:
            command = f'chmod ug+x ./runtime/{self.name}.sh'
            os.system(command)
            if os_is_windows():
                state = None
                try:
                    command = fr'"%ProgramFiles%\Git\bin\bash.exe" -c "cd {self.directory} && nohup ./{self.name}.sh > {self.name}.log 2>&1"'
                    print(command)
                    r = subprocess.Popen(command, shell=True)
                    state = 0
                except Exception as e:
                    print(e)
                    state = 1
            else:
                command = f'cd {self.directory} && nohup ./{self.name}.sh > {self.name}.log 2>&1'
                print(command)
                state = os.system(f'{command} &')

            logfile = path_expand(f"{self.directory}/{self.name}.log")

        started = False
        while started:
            os.system("sync")
            started = os.path.exists(logfile)
            print("STARTED")
            if not started:
                time.sleep(0.1)

        return state

    def clear(self):
        """
        clears all leftover log files from past runs

        :return: does not return anything
        :rtype: None
        """
        content = None
        try:
            source = f'~/experiment/{self.name}/{self.name}.log'
            destination = f"{self.name}.log"
            Shell.run(f"rm -f {destination}")
            Shell.run(f"rm -f {source}")
        except Exception as e:
            Console.error(e, traceflag=True)

    def get_status(self, refresh=False):
        """
        fetches the log file of the job and returns the status of
        the job, which can be undefined, running, or done

        :param refresh: whether to copy the log file in case of changes
        :type refresh: bool
        :return: returns status, which is the progress of the job
        :rtype: str
        """
        status = "ready"
        try:
            log = self.get_log(refresh=refresh)
            lines = Shell.find_lines_with(log, "# cloudmesh")
            if len(lines) > 0:
                status = lines[-1].split("status=")[1]
                status = status.split(" ")[0]
        except:  # noqa: E722
            pass

        return status

    def get_progress(self, refresh=False):
        """
        fetch the log file of the job and read the log file to check
        for the current completeness of the job

        :param refresh: whether to copy the log file in case of changes
        :type refresh: bool
        :return: value from 0 to 100 which reflects completeness of job
        :rtype: int
        """
        progress = 0
        try:
            log = self.get_log(refresh=refresh).splitlines()
            lines = Shell.find_lines_with(log, "# cloudmesh")
            for i in range(len(lines)-1, -1, -1):
                line = lines[i]
                if "progress=" in line:
                    progress = line.split("progress=")[1]
                    progress = progress.split(' ',1)[0]
                    progress = int(progress)
                    return int(progress)
        except Exception as e:  # noqa: E722
            pass

        return int(progress)

    def get_log(self, refresh=True):
        """
        copy the log file, sync, and read the contents of the file to
        return the contents as a string

        :param refresh: whether to copy the log file in case of changes
        :type refresh: bool
        :return: the contents of the log file in string format
        :rtype: str
        """
        content = None
        try:
            if refresh:
                command = f"cp {self.directory}/{self.name}.log ./runtime/{self.name}.log"
                print(command)
                os.system(command)
                os.system("sync")  # tested and returns 0
            content = readfile(f"runtime/{self.name}.log")
        except:  # noqa: E722
            pass
        return content

    def sync(self):
        """
        copies the shell script to the experiment directory and
        ensures that the file is copied with the sync command

        :return: 0 or 1 depending on success of command
        :rtype: int
        """
        self.mkdir_experimentdir()
        self.chmod()
        command = f"cp ./runtime/{self.name}{self.filetype} {self.directory}/."
        print(command)
        Shell.run(command)
        os.system("sync")
        r = os.system(command)
        return r

    def chmod(self):
        """
        changes the permissions and flags of the script to be
        run (shell or py file, ipynb not yet supported) so that
        the system can successfully execute the script

        :return: 0 or 1 depending on success of command
        :rtype: int
        """
        command = f'chmod ug+rx ./runtime/{self.name}{self.filetype}'
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
        return os.path.exists(path_expand(f'{self.directory}/{filename}'))

    def watch(self, period=10):
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
        while not finished:
            progress = int(self.get_progress(refresh=True))
            print(f"Progress {self.name}:", progress)
            finished = progress == 100
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
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"./runtime/{self.name}.log")
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            pid = lines[0].split("pid=")[1]
            pid = pid.split()[0]
            return pid
        return None

    def kill(self, period=1):
        """
        kills the job

        :param period: interval to use for waiting for log/pid
        :type period: float
        :returns:
            - pid - process identifier as str
            - child - child process as str
        """
        #
        # find logfile
        #

        logfile = f'runtime/{self.name}.log'
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
            time.sleep(period)
        pid = None
        while pid is None:
            time.sleep(period)
            pid = self.get_pid(refresh=True)

        print(pid.strip())
        pid = str(pid).strip()
        ps = subprocess.check_output('ps', shell=True, text=True)
        print(ps)
        r = None
        if os_is_windows():
            rs = []
            child = None
            results = ps.splitlines()
            for result in results:
                rs.append(result.split())
            print(rs)
            for result in rs:
                if result[1] == pid:
                    child = result[0]
            try:
                r = subprocess.check_output(fr'"%ProgramFiles%\Git\bin\bash.exe" -c "kill -9 {pid} {child}"', shell=True)
                print(r)
                #r = Shell.run(f'taskkill /PID {pid} /F')
            except Exception as e:
                print(e.output)
        else:
            command = f'pgrep -P {pid}'
            child = Shell.run(command).strip()
            command = f'kill -9 {pid} {child}'
            r = os.system(command)
            r = os.system(f'kill -9 {pid}')
        Console.msg(f"Killing {pid} {child}")
        print(r)
        if "No such process" in str(r):
            Console.warning(
                f"Process {pid} not found. It is likely it already completed.")
        return pid, child

    def create_script(self, exec=None):
        """
        creates a template
        for the slurm sbatch

        :param exec: command to be executed
        :type exec: str
        :return: name of script
        :rtype: str
        """
        filename = f"{self.name}.sh"
        if self.filetype == 'ipynb':
            output = exec.replace(".ipynb", "-output.ipynb")
            exec = f"papermill {exec} {output}"
        elif self.filetype == 'sh':
            pass
        elif self.filetype == 'py':
            exec = f'python {exec}'
        else:
            pass

        template = textwrap.dedent(
            f"""
            #!/bin/sh
            echo "# cloudmesh status=running progress=1 pid=$$"
            {exec}
            echo "# cloudmesh status=running progress=100 pid=$$"
            #
            """).strip()
        script = template.format(exec=exec)
        writefile(filename=filename, content=script)
        os.system(f"chmod a+x {filename}")
        return filename

    # this method is deprecated ....
    @staticmethod
    def create(filename=None, script=None, exec=None):
        """
        creates a template
        for the slurm sbatch

        :param filename: name of file that the script will be written to
        :type filename: str
        :param script: contents of script
        :type script: str
        :param exec: command to be executed
        :type exec: str
        :return: the contents of the script itself
        :rtype: str
        """

        if script is None and exec is None:
            Console.error("Script and executable cannot be used at the same time.")

        if script is not None:
            exec = script
        elif '.ipynb' in exec:
            output = exec.replace(".ipynb", "-output.ipynb")
            exec = f"papermill {exec} {output}"
        elif '.sh' in exec:
            pass
        elif '.py' in exec:
            exec = f'python {exec}'
        else:
            pass


        template = textwrap.dedent(
            f"""
            #!/bin/sh
            echo "# cloudmesh status=running progress=1 pid=$$"
            {exec}
            echo "# cloudmesh status=running progress=100 pid=$$"
            #
            """).strip()
        script = template.format(exec=exec)
        writefile(filename=filename, content=script)
        return script
