import os

# from cloudmesh.common FIND SOMETHING THAT READS TEXT FILES
import time

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.variables import Variables



class Job():

    def __init__(self, name=None,  label=None, **argv):
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

        #print(self.data)
        variables = Variables()
        # try:
        #    a,b,c, = self.name, self.host
        # except:
        #    Console.error("name, or host not set")
        #    raise ValueError

        variables = Variables()

        self.name = name
        if label is None:
            label = name

        #print("self.data", self.data)
        for key, value in self.data.items():
            setattr(self, key, value)

        if self.name is None:
            Console.error("Name is not defined")
            raise ValueError

        if "directory" in self.data:
            self.directory = self.data["directory"]
        else:
            self.directory = f"~/experiment/{self.name}"

        #print(self)

    def __str__(self):
        msg = []
        msg.append(f"name: {self.name}")
        msg.append(f"directory: {self.directory}")
        msg.append(f"data: {self.data}")
        msg.append(f"locals  {locals()}")
        return "\n".join(msg)

    @property
    def status(self):
        return self.get_status()

    def mkdir_local(self):
        command = f"mkdir -p {self.directory}"
        # print(command)
        os.system(command)

    def create_log(self):
        log = writefile(f'{self.name}.log', 'e')
        return log


    def run(self):
        self.mkdir_local()
        self.create_log()

        # command = f'chmod ug+x ./{self.name}.sh'
        # os.system(command)
        command = f"cd {self.directory} && nohup {self.name} > " \
                  f"{self.name}.log 2> {self.name}.err"
        print(command)
        state = os.system(command)
#        error = self.get_error()
        log = self.get_log()
        return state, log

    def get_status(self, refresh=False):
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"{self.name}.log", 'r')
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            status = lines[-1].split("status=")[1]
            status = status.split()[0]
            return status

    def get_progress(self, refresh=False):
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"{self.name}.log", 'r')
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            try:
                progress = lines[-1].split("progress=")[1]
                progress = progress.split()[0]
                return int(progress)
            except:
                return 0
        return 0

    # def get_error(self):
    #     command = f"scp{self.directory}/{self.name}.error {self.name}.error"
    #     print(command)
    #     os.system(command)
    #     content = readfile(f"{self.name}.error", 'r')
    #     return content

    def get_log(self):
        global status
        command = f"{self.directory}/{self.name}.log"
        print(command)
        os.system(command)
        content = readfile(f"{self.name}.log", 'r')
        return content


    # def sync(self, filepath):
    #     self.mkdir_local()
    #     command = f"scp ./{self.name}.sh {self.username}@{self.host}:{self.directory}/."
    #     print(command)
    #     r = os.system(command)
    #     return r


    def exists(self, filename):
        command = f"ls {self.directory}/{filename}"
        print(command)
        r = Shell.run(command)
        if "cannot access" in r:
            return False
        return True


    def watch(self, period=10):
        """waits and wathes every seconds in period, till the job has completed"""
        finished = False
        while not finished:
            progress = int(self.get_progress(refresh=True))
            finished = progress == 100
            if not finished:
                time.sleep(period)


    def get_pid(self, refresh=False):
        """get the pid from the job"""
        if refresh:
            log = self.get_log()
        else:
            log = readfile(f"{self.name}.log", 'r')
        lines = Shell.find_lines_with(log, "# cloudmesh")
        if len(lines) > 0:
            pid = lines[0].split("pid=")[1]
            pid = pid.split()[0]
            return pid
        return None


    def kill(self):
        """
        kills the job
        """
        pid = self.get_pid()
        command = f"kill -9 {pid}"
        print(command)
        r = Shell.run(command)
        print(r)
        if "No such process" in r:
            Console.warning(
                "Process {pid} not found. It is likely it already completed.")

j=Job(name='alex', directory='cm/cloudmesh-cc/cloudmesh/cc/localhost')
j.run()



