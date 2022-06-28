###############################################################
# pytest -v --capture=no tests/test_job_ssh.py
# pytest -v  tests/test_job_ssh.py
# pytest -v --capture=no  tests/test_job_ssh.py::TestJobssh::<METHODNAME>
###############################################################
import os

import pytest

from cloudmesh.cc.job.localhost.AlexJob import Job
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables

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

    def test_create_run(self):
        os.system("cp ./tests/run.sh .")
        assert os.path.isfile("./run.sh")

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

    def test_run(self):
        HEADING()
        global job

        Benchmark.Start()
        s, l, e = job.run()
        print("State:", s)
        # print(l)
        # print(e)

        Benchmark.Stop()

        assert s == 0

    def test_progress_status(self):
        HEADING()
        global job

        Benchmark.Start()
        job.get_log()
        progress = job.get_progress()
        print("Progress:", progress)
        status = job.get_status()
        print("Status:", status)
        Benchmark.Stop()

        assert progress == 100
        assert status == "done"

    def test_exists(self):
        HEADING()
        global job

        Benchmark.Start()
        wrong = job.exists(name)
        correct = job.exists(f"{name}.sh")
        Benchmark.Stop()

        assert not wrong
        assert correct

    def test_watch(self):
        HEADING()
        global job
        global username
        global host
        global name
        Benchmark.Start()
        os.remove("run.log")
        os.remove("run.error")
        job = Job(name=name, host=host, username=username)
        r = job.sync("./tests/run.sh")
        job.run()
        job.watch(period=1)
        status = job.get_status()
        Benchmark.Stop()
        assert status == "done"

    def test_kill(self):
        HEADING()
        global job
        global username
        global host
        global name
        Benchmark.Start()
        os.remove("run.log") if os.path.exists("run.log") else None
        os.remove("run.error") if os.path.exists("run.error") else None
        job = Job(name=name, host=host, username=username)
        r = job.sync("./tests/run.sh")
        job.run()
        pid = job.get_pid()
        job.kill()
        status = job.get_status()
        print ("Status", status)
        Benchmark.Stop()
        # assert status == "done"
        # check with ps if pid is running
