import os

# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
import time

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile


class Lsf:

    def __init__(self, host):
        """
        sets locations of LSF commands for the job

        :param host: device that the script will be run on
        :type host: str
        """
        if host.startswith("rivanna"):
            Console.error("Rivanna does not use LSF but SLURM")

            # self.slurm = "/opt/slurm/current/bin"
            # self.squeue = f"{self.slurm}/squeue"
            # self.sbatch = f"{self.slurm}/sbatch"
            # self.srun = f"{self.slurm}/srun"
        else:
            Console.error("LSF not yet set up for this host")


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
            self.directory = f'~/experiment/{self.name}'

        self.slurm = Lsf(self.host)

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
        script remotely. only works for slurm scripts, as slurm is
        hardcoded within the commands

        :returns:
            - state - undefined, running, or done
            - log - output of the job
            - job_id - the slurm job id of the job
        """
        self.mkdir_experimentdir()

        command = f'chmod ug+x ./{self.name}.sh'
        os.system(command)
        command = f'ssh {self.username}@{self.host} ' \
                  f'"cd {self.directory} && {self.slurm.sbatch} ' \
                  f'{self.name}.sh"'
        print(command)
        state = None
        # state = os.system(f'{command} &')
        try:
            r = Shell.run(f'{command}')
            state = 0
        except Exception as e:  # noqa: E722
            print(e)
            state = 1
        job_id = str(r).split()[-1]
        log = self.get_log()
        return state, log, job_id

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

    def get_log(self):
        """
        copy the remote log file and read the contents of the file to
        return the contents as a string

        :return: the contents of the log file in string format
        :rtype: str
        """
        command = f"scp {self.username}@{self.host}:{self.directory}/{self.name}.log {self.name}.log"
        print(command)
        os.system(command)
        content = readfile(f"{self.name}.log")
        return content

    def sync(self):
        """
        makes experiment dir and changes permissions, and then
        copies the shell script to remote host

        :return: 0 or 1 depending on success of command
        :rtype: int
        """
        self.mkdir_experimentdir()
        self.chmod()
        command = f"scp ./{self.name}.sh {self.username}@{self.host}:{self.directory}/."
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
            command = f"chmod ug+rx ./{self.name}.py"
        else:
            command = f"chmod ug+rx ./{self.name}.sh"
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
        until the job has completed

        :param period: time in seconds to check, as an interval
        :type period: float
        :return: does not return anything
        :rtype: None
        """
        finished = False
        while not finished:
            progress = int(self.get_progress(refresh=True))
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
        kills the job, assuming that job is slurm job

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
