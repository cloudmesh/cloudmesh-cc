import os

# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
import time

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile


class Slurm:

    def __init__(self, host):
        if host.startswith("rivanna"):
            self.slurm = "/opt/slurm/current/bin"
            self.squeue = f"{self.slurm}/squeue"
            self.sbatch = f"{self.slurm}/sbatch"
            self.srun = f"{self.slurm}/srun"
        else:
            Console.error("Slurm not yet set up for this host")


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
        self.name = name or "job"
        self.directory = directory

        if label is None:
            self.label = name or "job"
        else:
            self.label = name

        # print("self.data", self.data)
        for key, value in self.data.items():
            setattr(self, key, value)

        if self.username is None:
            self.username = os.environ["USERNAME"]

        if self.host is None:
            self.host = "localhost"

        if self.directory is None:
            self.directory = f'~/experiment/{self.name}'

        self.slurm = Slurm(self.host)

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
        for line in str(r).splitlines():
            if line.startswith('Submitted'):
                job_id = line.split()[-1]
        return state, job_id

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
            except:  # noqa: E722
                return 0
        return 0

    # def get_error(self):
    #     command = f"scp {self.username}@{self.host}:{self.directory}/{self.name}.error {self.name}.error"
    #     print(command)
    #     os.system(command)
    #     content = readfile(f"{self.name}.error")
    #     return content

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

    def kill(self, period=1, job_id=None):
        """
        kills the job
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
            time.sleep(2)
        pid = None
        while pid is None:
            time.sleep(1)
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
