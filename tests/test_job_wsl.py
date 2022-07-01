###############################################################
# pytest -v -x --capture=no tests/test_job_wsl.py
# pytest -v  tests/test_job_wsl.py
# pytest -v --capture=no  tests/test_job_wsl.py::TestJobssh::<METHODNAME>
###############################################################
import os
import time

import pytest

from cloudmesh.cc.job.wsl.Job import Job
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell

from cloudmesh.common.systeminfo import os_is_windows
variables = Variables()

host = "localhost"
if os_is_windows():
    username = os.environ["USERNAME"]
else:
    username = os.environ["USER"]

job = None


@pytest.mark.incremental
class TestJoblocalhost:

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
        Benchmark.Start()
        name = "run"
        job = Job(name=name, host=host, username=username)
        Benchmark.Stop()
        assert job.name == name
        assert job.host == host
        assert job.username == username

    def test_sync(self):
        HEADING()
        global job

        Benchmark.Start()
        print(type(job))
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
        # job = Job(name="run", host=host, username=username)
        r = job.sync()

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

        Benchmark.Start()
        jobWait = Job(name="wait", host=host, username=username)
        r = jobWait.sync()

        s, l, e = jobWait.run()

        jobWait.watch(period=1)
        log = jobWait.get_log()
        progress = jobWait.get_progress()
        print("Progress:", progress)
        status = jobWait.get_status(refresh=True)
        print("Status:", status)
        assert log is not None
        assert s == 0
        assert progress == 100
        assert status == "done"

        Benchmark.Stop()

    def test_exists(self):
        HEADING()
        global job

        name = "run"
        Benchmark.Start()
        wrong = job.exists(name)
        correct = job.exists(f"{name}.sh")
        Benchmark.Stop()

        assert not wrong
        assert correct

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

        os.system("rm -r ~/experiment")
        os.system("cp ./tests/run.sh .")
        os.system("cp ./tests/wait.sh .")

        name = "wait"

        os.system("rm -f ./wait.log")
        os.system("rm -f ./wait.error")

        Benchmark.Start()
        # job = Job(name="run", host=host, username=username)
        print(job)
        r = job.sync()
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
