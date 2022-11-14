"""SSH Job."""
import os
import subprocess
import time
import textwrap

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile


class Job:
    """SSH Job."""

    def __init__(self, **argv):
        r"""Initialize the job.

        cms set username=abc123

        creates a job by passing either a dict with \*\*dict or named arguments
        attribute1 = value1, ...

        :param name:
        :param username:
        :param host:
        :param label:
        :param directory:
        :param argv:
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
        #self.filetype = self.script_type(self.name)

        if self.script is None and self.exec is not None:
            self.script = self.create_script(self.exec)

    def script_type(self, name):
        """Return the filename type based on the ending.

        Uses the inputted name of script to return the
        corresponding file extension that is run, such as
        shell script, jupyter notebook, or python file

        :param name: the name of the script
        :type name: str
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
        """Return the string object of the job.

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
        """Return the status.

        exactly the same as get_status but duplicated to provide as
        a shortened-named, alternative call

        :return: the status of job
        :rtype: str
        """
        return self.get_status()

    def mkdir_experimentdir(self):
        """Create the experiment directory.

        creates remote experiment directory to contain job files such as
        yaml file, log file, and pertinent script to be run
        like sh script or ipynb or py

        :return: does not return anything
        :rtype: None
        """
        command = f'ssh {self.username}@{self.host} "mkdir -p {self.directory}"'
        print(command)
        os.system(command)

    def run(self):
        """Run the Job.

        runs the job by making script executable and running the
        job remotely.

        :returns:
            - state - undefined, running, or done
            - log - the output of the job
        """
        self.mkdir_experimentdir()

        command = f'ssh {self.username}@{self.host} "chmod ug+x {self.directory}/{self.name}{self.filetype}"'
        print(command)
        os.system(command)
        if os_is_windows():

            if self.filetype == ".py":
                try:
                    if hasattr(self, 'venv'):
                        command = f'ssh {self.username}@{self.host} "cd {self.directory} ; source activate {self.venv} ; python ./{self.name}.py > {self.name}.log 2>&1 &"'
                    else:
                        command = f'ssh {self.username}@{self.host} "cd {self.directory} ; python ./{self.name}.py > {self.name}.log 2>&1 &"'
                    print(command)
                    r = subprocess.Popen(command, shell=True)
                    state = 0
                except Exception as e:
                    print(e)
                    state = 1

            elif self.filetype == ".ipynb":
                try:
                    command = f'ssh {self.username}@{self.host} "cd {self.directory} ; papermill ./{self.name}.ipynb > {self.name}.log 2>&1 &"'
                    print(command)
                    r = subprocess.Popen(command, shell=True)
                    state = 0
                except Exception as e:
                    print(e)
                    state = 1

            else:
                try:
                    command = f'ssh {self.username}@{self.host} "cd {self.directory} ; nohup ./{self.name}.sh > {self.name}.log 2>&1 &"'
                    print(command)
                    r = subprocess.Popen(command, shell=True)
                    state = 0
                except Exception as e:
                    print(e)
                    state = 1

        else:

            if self.filetype == ".py":
                command = f'ssh {self.username}@{self.host} "cd {self.directory} && python ./{self.name}.py > {self.name}.log 2>&1"'
                print(command)
                state = os.system(f'{command} &')

            elif self.filetype == ".ipynb":
                command = f'ssh {self.username}@{self.host} "cd {self.directory} && papermill ./{self.name}.ipynb > {self.name}.log 2>&1"'
                print(command)
                state = os.system(f'{command} &')

            else:
                command = f'ssh {self.username}@{self.host} "cd {self.directory} && nohup ./{self.name}.sh > {self.name}.log 2>&1"'
                print(command)
                state = os.system(f'{command} &')

        log = self.get_log()
        return state, log

    def clear(self):
        """Clear all leftover log files from past runs.

        clears all leftover log files from past runs

        :return: does not return anything
        :rtype: None
        """
        try:
            source = f'~/experiment/{self.name}/{self.name}.log'
            destination = f"{self.name}.log"
            Shell.run(f"rm -f {destination}")
            Shell.run(f'ssh {self.username}@{self.host} "rm -f {source}"')
        except Exception as e:
            Console.error(e, traceflag=True)

    def get_status(self, refresh=False):
        """Get the status of the job.

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
        """Get the progress of the job.

        fetches the log file of the job and reads the log file to check
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
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i]
                if "progress=" in line:
                    progress = line.split("progress=")[1]
                    progress = progress.split(' ', 1)[0]
                    progress = int(progress)
                    return int(progress)
        except Exception as e:  # noqa: E722
            pass

        return int(progress)

    def get_log(self, refresh=True):
        """Get the log file of the job.

        copy the remote log file and read the contents of the file to
        return the contents as a string

        :return: the contents of the log file in string format
        :rtype: str
        """
        content = None
        time.sleep(0.5)
        try:
            if refresh:
                command = f"scp {self.username}@{self.host}:{self.directory}/{self.name}.log ./runtime/{self.name}.log"
                print(command)
                os.system(command)
                os.system("sync")  # tested and returns 0
            content = readfile(f"runtime/{self.name}.log")
        except:  # noqa: E722
            pass
        return content

    def sync(self):
        """Syncronise the current directory with the remote.

        makes experiment dir and changes permissions, and then
        copies the shell script to remote host

        :return: 0 or 1 depending on success of command
        :rtype: int
        """
        self.mkdir_experimentdir()
        self.chmod()

        command = f"scp ./runtime/{self.name}{self.filetype} {self.username}@{self.host}:{self.directory}/."
        print(command)
        r = os.system(command)
        return r

    def chmod(self):
        """Fix permissions.

        changes the permissions and flags of the script to be
        run (shell or py file, ipynb not yet supported) so that
        the system can successfully execute the script

        :return: 0 or 1 depending on success of command
        :rtype: int
        """
        command = f"chmod ug+rx ./runtime/{self.name}{self.filetype}"
        print(command)
        r = os.system(command)
        return r

    def exists(self, filename):
        """Check if the filname exists.

        used to check if the file is existing within the remote experiment
        directory

        :param filename: the name of the script, including file extension
        :type filename: str
        :return: True if the file exists and False if it doesnt
        :rtype: bool
        """
        command = f'ssh {self.username}@{self.host} "ls {self.directory}/{filename}"'
        print(command)
        r = Shell.run(command)
        print(r)
        if "cannot access" in r:
            return False
        return True

    def watch(self, period=10):
        """Watch the job and check for changes in the given period.

        waits and watches for progress to reach 100, on interval basis
        specified in the period in seconds,
        until the job has completed

        :param period: time in seconds to check, as an interval
        :type period: float
        :return: does not return anything
        :rtype: None
        """
        finished = False
        while not finished:
            progress = self.get_progress(refresh=True)
            print (f"Progress {self.name}:", progress)
            finished = progress == 100
            if not finished:
                time.sleep(period)

    def get_pid(self, refresh=False):
        """Watch the job and check for changes in the given period.

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

    def kill(self, period=3):
        """Kill the job.

        :param period: interval to use for waiting for log/pid
        :type period: float
        :returns:
            - pid - process id of the script
            - child - child of the script
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

    def create_script(self, exec=None):
        """Create a template for the script.

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
            echo "# cloudmesh status=done progress=100 pid=$$"
            #
            """).strip()
        script = template.format(exec=exec)
        writefile(filename=filename, content=script)
        os.system(f"chmod a+x {filename}")
        return filename

