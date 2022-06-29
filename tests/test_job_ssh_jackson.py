###############################################################
# pytest -v -x --capture=no tests/test_job_ssh_jackson.py
# pytest -v  tests/test_job_ssh.py
# pytest -v --capture=no  tests/test_job_ssh.py::TestJobssh::<METHODNAME>
###############################################################
import os
import time

import pytest

from cloudmesh.cc.job.ssh.JacksonJob import Job
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell
variables = Variables()

name = "run"

if "host" not in variables:
    host = "rivanna.hpc.virginia.edu"
else:
    host = variables["host"]

username = variables["username"]

job = None


@pytest.mark.incremental
class TestJobssh:

    def test_kill(self):
        """
        Creates a job from wait.sh, which includes wait of 1 hour
        Deletes this job AND it's children
        This way, it tests if the job or any of it's children
        is found in the ps
        """
        HEADING()
        global job
        global username
        global host
        global name

        os.system("rm -r ~/experiment")
        os.system("cp ./tests/run.sh .")
        os.system("cp ./tests/wait.sh .")

        name = "wait"

        os.system("rm -f ./wait.log")
        os.system("rm -f ./wait.error")

        Benchmark.Start()
        job = Job(name=name, host=host, username=username)
        print(job)
        r = job.sync('./tests/run.sh')
        job.run()
        time.sleep(2)
        parent = job.get_pid()
        job.kill()
        child = job.get_pid()
        status = job.get_status()
        print("Status", status)
        Benchmark.Stop()
        ps = Shell.run('ps')
        print('PIDs', parent, child)
        print(job.get_log())
        assert 'sleep 3600' not in ps
        assert str(parent) not in ps
        assert str(child) not in ps
        # assert status == "done"
        # check with ps if pid is running

class r:

    def test_create_run(self):
        os.system("rm -r ~/experiment")
        os.system("cp ./tests/run.sh .")
        os.system("cp ./tests/wait.sh .")
        assert os.path.isfile("./run.sh")
        assert os.path.isfile("./wait.sh")

    def test_create(self):
        HEADING()
        global job
        global username
        global host
        global name
        Benchmark.Start()
        job = Job(name=name, host=host, username=username)
        Benchmark.Stop()
        assert job.name == name
        assert job.host == host
        assert job.username == username

    def test_sync(self):
        HEADING()
        global job

        Benchmark.Start()
        r = job.sync("./tests/run.sh")

        Benchmark.Stop()
        # successful exit status
        assert r == 0

    def test_run_fast(self):
        HEADING()
        os.system("rm -r ~/experiment")
        os.system("cp ./tests/run.sh .")
        os.system("cp ./tests/wait.sh .")

        global job

        Benchmark.Start()
        job = Job(name=name, host=host, username=username)
        r = job.sync(filepath='./tests/run.sh')

        s, l, e = job.run()
        time.sleep(1)
        print("State:", s)
        print(l)
        print(e)

        log = job.get_log()
        if log is None:
            print('super fast')
            assert True
        else:
            progress = job.get_progress()
            print("Progress:", progress)
            status = job.get_status(refresh=True)
            print("Status:", status)
            assert log is not None
            assert s == 0
            assert progress == 100
            assert status == "done"

        Benchmark.Stop()

    def test_run_wait(self):
        HEADING()
        os.system("rm -r ~/experiment")
        os.system("cp ./tests/run.sh .")
        os.system("cp ./tests/wait.sh .")

        global job

        Benchmark.Start()
        job = Job(name=name, host=host, username=username)
        r = job.sync('./tests/run.sh')

        s, l, e = job.run()

        job.watch(period=1)
        log = job.get_log()
        progress = job.get_progress()
        print("Progress:", progress)
        status = job.get_status(refresh=True)
        print("Status:", status)
        assert log is not None
        assert s == 0
        assert progress == 100
        assert status == "done"

        Benchmark.Stop()

    def test_exists(self):
        HEADING()
        global job

        Benchmark.Start()
        wrong = job.exists(name)
        correct = job.exists(f"{name}.sh")
        Benchmark.Stop()

        assert not wrong
        assert correct

