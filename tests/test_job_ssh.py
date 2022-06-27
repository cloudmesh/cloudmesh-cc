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


variables = Variables()

name="run"
host="rivanna.hpc.virginia.edu"
username=variables["username"]

job = None



@pytest.mark.incremental
class TestJobssh:

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
        r = job.sync("~/cm/cloudmesh-cc/cloudmesh/cc/job/ssh/run")

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
