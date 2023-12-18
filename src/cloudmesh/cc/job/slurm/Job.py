"""SLURM job."""
import os

import time
import textwrap

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile


class Slurm:
    """Slurm Job."""

    def __init__(self, host):
        """Initialize the job.

        Set locations of slurm commands for the job.

        Args:
            host (str): device that the script will be run on
        """
        if host.startswith("rivanna"):
            self.slurm = "/opt/slurm/current/bin"
            self.squeue = f"{self.slurm}/squeue"
            self.sbatch = f"{self.slurm}/sbatch"
            self.srun = f"{self.slurm}/srun"
        else:
            Console.error("Slurm not yet set up for this host")


class Job:
    """SLURM job."""

    def __init__(self, **argv):
        r"""Initialize the job.

        cms set username=abc123

        creates a job by passing either a dict with \*\*dict or named arguments
        attribute1 = value1, ...

        Args:
            data: parameters and specifications of job, such as name

        Returns:
            None: nothing
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

        self.username = self.username or Shell.user()
        self.host = self.host or "localhost"
        self.directory = self.directory or f'~/experiment/{self.name}'

        self.kind = "local"
        self.label = self.label or self.name
        self.filetype = self.script_type(self.name)

        if self.script is None and self.exec is not None:
            self.script = self.create_script(self.exec)

        self.slurm = Slurm(self.host)

        Shell.mkdir(Shell.map_filename(self.directory).path)
        if not os.path.isdir(Shell.map_filename('~/.cloudmesh/workflow').path):
            Shell.mkdir(Shell.map_filename('~/.cloudmesh/workflow').path)

    def script_type(self, name):
        """Return the filename type based on the ending.

        Uses the inputted name of script to return the
        corresponding file extension that is run, such as
        shell script, jupyter notebook, or python file

        Args:
            name (str): the name of the script

        Returns:
            str: file extension of script
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

        Returns:
            str: description and specifications of job in string format
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

        Returns:
            str: the status of job
        """
        return self.get_status()

    def clean(self):
        """Delete the remote experiment directory.

        Returns:
            None: nothing
        """
        command = f'ssh {self.username}@{self.host} "rm -rf {self.directory}"'
        print(command)
        os.system(command)

    def mkdir_experimentdir(self):
        """Create the experiment directory.

        creates remote experiment directory to contain job files such as
        yaml file, log file, and pertinent script to be run
        like sh script or ipynb or py

        Returns:
            None: does not return anything
        """
        command = f'ssh {self.username}@{self.host} "mkdir -p {self.directory}"'
        print(command)
        os.system(command)

    def run(self):
        """Run the job.

        runs the job by making script executable and running the
        slurm job remotely.

        Returns:
            - state - undefined, running, or done - job_id - the slurm
            job id of the job
        """
        self.mkdir_experimentdir()

        command = f'chmod ug+x ./runtime/{self.name}.sh'
        os.system(command)
        command = f'ssh {self.username}@{self.host} ' \
                  f'"cd {self.directory} && {self.slurm.sbatch} ' \
                  f'{self.name}.sh"'
        print(command)
        state = None
        # state = os.system(f'{command} &')
        r = None
        try:
            r = Shell.run(f'{command}')
            state = 0
        except Exception as e:  # noqa: E722
            print(e.output)
            state = 1
        for line in str(r).splitlines():
            if line.startswith('Submitted'):
                job_id = line.split()[-1]
        return state, job_id

    def clear(self):
        """Clear all leftover log files from past runs.

        Returns:
            None: does not return anything
        """
        content = None
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

        Args:
            refresh (bool): whether to copy the log file in case of
                changes

        Returns:
            str: returns status, which is the progress of the job
        """
        status = "ready"
        try:
            log = self.get_log(refresh=refresh)
            lines = Shell.find_lines_with(log, "# cloudmesh")
            if len(lines) > 0:
                status = lines[-1].split("status=")[1]
                status = status.split(" ")[0]
                print(status)
        except:  # noqa: E722
            pass

        return status

    def get_progress(self, refresh=False):
        """Get the progress of the job.

        fetches the log file of the job and reads the log file to check
        for the current completeness of the job

        Args:
            refresh (bool): whether to copy the log file in case of
                changes

        Returns:
            int: value from 0 to 100 which reflects completeness of job
        """
        progress = 0
        try:
            log = self.get_log(refresh=refresh).splitlines()
            for line in log:
                line = line.rstrip('\x00')
            lines = Shell.find_lines_with(log, "# cloudmesh")
            for i in range(len(lines)-1, -1, -1):
                line = lines[i]
                if "progress=" in line:
                    progress = line.split("progress=")[1]
                    progress = progress.split(' ',1)[0]
                    progress = int(progress)
                    return int(progress)
        except Exception as e:  # noqa: E722
            print(e)
            pass

        return int(progress)

    def get_log(self, refresh=True):
        """Get the log of the job.

        copy the remote log file and read the contents of the file to
        return the contents as a string

        Returns:
            str: the contents of the log file in string format
        """
        content = None
        try:
            if refresh:
                command = f"scp {self.username}@{self.host}:{self.directory}/{self.name}.log ./runtime/{self.name}.log"
                print(command)
                os.system(command)
            content = readfile(f"./runtime/{self.name}.log")
        except:  # noqa: E722
            pass
        return content

    def sync(self):
        """Syncronise the current directory with the remote.

        makes experiment dir and changes permissions, and then
        copies the shell script to remote host

        Returns:
            int: 0 or 1 depending on success of command
        """
        self.clean()
        self.mkdir_experimentdir()
        self.chmod()
        command = f"scp ./runtime/{self.name}.sh {self.username}@{self.host}:{self.directory}/."
        print(command)
        r = os.system(command)
        return r

    def chmod(self):
        """Fix permissions.

        changes the permissions and flags of the script to be
        run (shell or py file, ipynb not yet supported) so that
        the system can successfully execute the script

        Returns:
            int: 0 or 1 depending on success of command
        """
        if self.filetype == "python":
            command = f"chmod ug+rx ./runtime/{self.name}.py"
        else:
            command = f"chmod ug+rx ./runtime/{self.name}.sh"
        print(command)
        r = os.system(command)
        return r

    def exists(self, filename):
        """Check if the filname exists.

        used to check if the file is existing within the remote experiment
        directory

        Args:
            filename (str): the name of the script, including file
                extension

        Returns:
            bool: True if the file exists and False if it doesnt
        """
        command = f'ssh {self.username}@{self.host} "ls {self.directory}/{filename}"'
        print(command)
        r = Shell.run(command)
        if "cannot access" in r:
            return False
        return True

    def watch(self, period=10):
        """Watch the job and check for changes in the given period.

        waits and watches for progress to reach 100, on interval basis
        specified in the period in seconds,
        until the job has completed

        Args:
            period (float): time in seconds to check, as an interval

        Returns:
            None: does not return anything
        """
        finished = False
        progress = 0
        while not finished:
            try:
                progress = int(self.get_progress(refresh=True))
            except:
                pass
            finished = progress == 100
            if not finished:
                time.sleep(period)

    def get_pid(self, refresh=False):
        """Get the pid that the job is running within.

        Args:
            refresh (bool): whether to retrieve the latest log

        Returns:
            str: the pid (process identifier)
        """
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

    def kill(self, period=1, job_id=None):
        """Kill the job.

        Args:
            period (float): interval to use for waiting for log/pid
            job_id (str): id of slurm job

        Returns:
            str: output of squeue command
        """
        if job_id is None:
            Console.error("No job_id supplied")
            return
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

        command = f'ssh {self.username}@{self.host} "scancel {job_id}"'
        print(command)
        r = Shell.run(command)
        command = f'ssh {self.username}@{self.host} "squeue -j {job_id}"'
        print(command)
        r = Shell.run(command)
        # if "No such process" in r:
        #     Console.warning(
        #         f"Process {pid} not found. It is likely it already completed.")
        return r

    def create(self,
               command,
               file,
               jobname,
               card_name,
               gpu_count,
               system_partition,
               time):
        """Create a template for slurm sbatch.

        Args:
            command: command to be executed
            file: name of file
            jobname: name of job
            card_name: name of graphics card that job will be run on
            gpu_count: number of gpus
            system_partition: partition on which job will be run
            time: maximum time limit for slurm job

        Returns:
            None: nothing
        """
        script = """\
            #!/usr/bin/env bash
        
            #SBATCH --job-name=mlcommons-eq-{card_name}-{gpu_count}
            #SBATCH --output=%u-%j.out
            #SBATCH --partition={system.partition}
            #SBATCH -c {cpu_num}
            #SBATCH --mem={mem}
            #SBATCH --time={time}
            #SBATCH --gres=gpu:{card_name}:{gpu_count}
            #SBATCH --mail-user=%u@virginia.edu
            #SBATCH --mail-type=ALL
            #SBATCH --account={user.account}
        
            python {filename}
            """

        data = {
            "name": "mnl_mnist",
            "filename": "mnl_mnist.py",
            "partition": "dev",
            "cardname": "a100",
            "gpu_count": 1
        }

        writefile(f"{jobname}.sh", script.format(**data))
        script += f"\n{command}"


    def create_script(self, exec=None):
        """Create a template for the slurm sbatch with progress.

        Args:
            exec (str): command to be executed

        Returns:
            str: name of script
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

