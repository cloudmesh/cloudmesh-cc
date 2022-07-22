import os
import subprocess
import time

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.common.systeminfo import os_is_windows


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

    def mkdir_local(self):
        command = f'mkdir -p {self.directory}'
        os.system(command)

    @property
    def status(self):
        return self.get_status()

    def mkdir_experimentdir(self):
        if os_is_windows():
            win_directory = Shell.map_filename(self.directory).path
            # self.directory = self.directory.replace('~','%homepath%')
            command = f'mkdir "{win_directory}"'
        else:
            command = f'mkdir -p {self.directory}'
        print(command)
        os.system(command)

    def run(self):
        self.mkdir_experimentdir()

        command = f'chmod ug+x ./{self.name}.sh'
        os.system(command)
        if os_is_windows():
            # command = fr'''"\"%ProgramFiles%/Git/bin/bash.exe\" -c \"cd {self.directory} && sh ./{self.name}.sh > {self.name}.log 2>&1\""'''
            # command = f'''cmd.exe /c start "" "%ProgramFiles%\"/Git/bin/bash.exe\" -c \"cd {self.directory} && nohup ./{self.name}.sh > {self.name}.log 2>&1"'''
            state = None
            try:
                #r = Shell.run(fr'"%ProgramFiles%\Git\bin\bash.exe" -c "cd {self.directory} && nohup ./{self.name}.sh > {self.name}.log 2>&1"')
                r = subprocess.Popen(fr'"%ProgramFiles%\Git\bin\bash.exe" -c "cd {self.directory} && nohup ./{self.name}.sh > {self.name}.log 2>&1"', shell=True)
                state = 0
            except Exception as e:
                print(e)
                state = 1
        else:
            command = f'cd {self.directory} && nohup ./{self.name}.sh > {self.name}.log 2>&1'
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

        return state

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
        content = None
        try:
            if refresh:
                command = f"cp {self.directory}/{self.name}.log {self.name}.log"
                print(command)
                os.system(command)
                os.system("sync")  # tested and returns 0
            content = readfile(f"{self.name}.log")
        except:  # noqa: E722
            pass
        return content

    def sync(self):
        self.mkdir_experimentdir()
        Shell.run(f"chmod ug+rx ./{self.name}.sh")
        command = f"cp {self.name}.sh {self.directory}/."
        print(command)
        Shell.run(command)
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
            print(f"Progress {self.name}:", progress)
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

        print('IM DOING TESTING HERE')
        print(pid.strip())
        pid = str(pid).strip()
        print('printed pid ??')
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
