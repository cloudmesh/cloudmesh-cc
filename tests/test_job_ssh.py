###############################################################
# pytest -v --capture=no tests/test_job_ssh.py
# pytest -v  tests/test_job_ssh.py
# pytest -v --capture=no  tests/test_job_ssh.py::TestJobssh::<METHODNAME>
###############################################################
import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.cc.job.ssh.Job import Job
from cloudmesh.common.variables import Variables
import os

variables = Variables()

name="run"

if "host" not in variables:
    host = "rivanna.hpc.virginia.edu"
else:
    host=variables["host"]

username=variables["username"]

job = None


@pytest.mark.incremental
class TestJobssh:

    def test_create_run(self):
        os.system("cp ./tests/run.sh .")
        assert os.path.isfile("./run.sh")

    def test_create(self):
        HEADING()
        global job
        global variables
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
        global variables
        global username
        global host
        global name

        Benchmark.Start()
        r = job.sync("./tests/run.sh")

        Benchmark.Stop()
        # successful exit status
        assert r == 0

    def test_run(self):
        HEADING()
        global job
        global variables

        Benchmark.Start()
        s,l,e = job.run()
        print(s)
        # print(l)
        # print(e)

        Benchmark.Stop()

        assert s == 0

    def test_progress_status(self):
        HEADING()
        global job
        global variables

        Benchmark.Start()
        job.get_log()
        prog = job.get_progress()
        print("PROGRESS",prog)
        status = job.get_status()
        print("STATUS",status)
        Benchmark.Stop()

        assert prog == "100"
        assert status == "done"
