import os

import time
import textwrap

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile


class Slurm:

    def __init__(self, host):
        """
        sets locations of slurm commands for the job
        :param host: device that the script will be run on
        :type host: str
        """
        if host.startswith("rivanna"):
            self.slurm = "/opt/slurm/current/bin"
            self.squeue = f"{self.slurm}/squeue"
            self.sbatch = f"{self.slurm}/sbatch"
            self.srun = f"{self.slurm}/srun"
        else:
            Console.error("Slurm not yet set up for this host")


class Job:

    def __init__(self, **argv):
        """
        cms set username=abc123

        creates a job by passing either a dict with **dict or named arguments
        attribute1 = value1, ...

        :param data: parameters and specifications of job, such as name
        :type data:
        :return: nothing
        :rtype: None
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

    def script_type(self, name):
        """
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

    def clean(self):
        """
        deletes the remote experiment directory
        :return: nothing
        :rtype: None
        """
        command = f'ssh {self.username}@{self.host} "rm -rf {self.directory}"'
        print(command)
        os.system(command)

    def mkdir_experimentdir(self):
        """
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
        """
        runs the job by making script executable and running the
        slurm job remotely.
        :returns:
            - state - undefined, running, or done
            - job_id - the slurm job id of the job
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
            Shell.run(f'ssh {self.username}@{self.host} "rm -f {source}"')
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
                print(status)
        except:  # noqa: E722
            pass

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
        """
        copy the remote log file and read the contents of the file to
        return the contents as a string
        :return: the contents of the log file in string format
        :rtype: str
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
        """
        makes experiment dir and changes permissions, and then
        copies the shell script to remote host
        :return: 0 or 1 depending on success of command
        :rtype: int
        """
        self.clean()
        self.mkdir_experimentdir()
        self.chmod()
        command = f"scp ./runtime/{self.name}.sh {self.username}@{self.host}:{self.directory}/."
        print(command)
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
        if self.filetype == "python":
            command = f"chmod ug+rx ./runtime/{self.name}.py"
        else:
            command = f"chmod ug+rx ./runtime/{self.name}.sh"
        print(command)
        r = os.system(command)
        return r

    def exists(self, filename):
        """
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
        if "cannot access" in r:
            return False
        return True

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
            log = readfile(f"{self.name}.log")
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            pid = lines[0].split("pid=")[1]
            pid = pid.split()[0]
            return pid
        return None

    def kill(self, period=1, job_id=None):
        """
        kills the slurm job
        :param period: interval to use for waiting for log/pid
        :type period: float
        :param job_id: id of slurm job
        :type job_id: str
        :return: output of squeue command
        :rtype: str
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

    def create(self, command, file, jobname, card_name, gpu_count, system_partition, time):
        """
        creates a template
        for the slurm sbatch
        :param command: command to be executed
        :param file: name of file
        :param jobname: name of job
        :param card_name: name of graphics card that job will be run on
        :param gpu_count: number of gpus
        :param system_partition: partition on which job will be run
        :param time: maximum time limit for slurm job
        :return: nothing
        :rtype: None
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
        # TODO add sbatch pragmas
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

