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


        self.username = self.username or Shell.user()
        self.host = self.host or "localhost"
        self.directory = self.directory or f'~/experiment/{self.name}'

        self.kind = "local"
        self.label = self.label or self.name
        self.filetype = self.script_type(self.name)

        if self.script is None and self.exec is not None:
            self.script = self.create_script(self.exec)

        #if self.exec is None and self.script is None:
        #    Console.warning("either exec or script must be set")

    def script_type(self, name):
        kind = "sh"
        if name is None:
            return kind
        for kind in ["sh", "ipynb", "sh", "py"]:
            if name.endswith(f".{kind}"):
                return kind
        return "os"


    def __str__(self):
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

        logfile = path_expand(f"{self.directory}/{self.name}.sh")

        started = False
        while started:
            os.system("sync")
            started = os.path.exists(logfile)
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
        self.chmod()
        command = f"cp {self.name}.sh {self.directory}/."
        print(command)
        Shell.run(command)
        os.system("sync")
        r = os.system(command)
        return r

    def chmod(self):
        if self.filetype == "python":
            command = f"chmod ug+rx ./{self.name}.py"
        else:
            command = f"chmod ug+rx ./{self.name}.sh"
        print(command)
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

    def create_script(self, exec=None):
        """
        creates a template
        for the slurm sbatch
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


    @staticmethod
    def create(filename=None, script=None, exec=None):
        """
        creates a template
        for the slurm sbatch
        """

        if script is None and exec is None:
            Console.error("Script and executable can not be used at the same time.")

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
