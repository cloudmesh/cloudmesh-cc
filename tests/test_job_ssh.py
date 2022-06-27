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

job = None

variables = Variables()


@pytest.mark.incremental
class TestJobssh:

    def test_run(self):
        HEADING()
        global job
        global variables
        Benchmark.Start()
        job = Job(name="run",host="rivanna.hpc.virginia.edu",username=variables["username"])
        # job.sync()
        Benchmark.Stop()
        # VERBOSE(result)

        assert True

class a:
    def test_run(self):
        HEADING()
        global job
        global variables

        Benchmark.Start()
        s,l,e = job.run()
        print(s)
        print(l)
        print(e)

        Benchmark.Stop()
        assert True

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc")
