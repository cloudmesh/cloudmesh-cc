###############################################################
# pytest -v -x --capture=no tests/test_job_localhost_jackson.py
# pytest -v  tests/test_job_ssh.py
# pytest -v --capture=no  tests/test_job_ssh.py::TestJobssh::<METHODNAME>
###############################################################
import os
import time

import pytest

from cloudmesh.cc.job.localhost.JacksonJob import Job
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell

@pytest.mark.incremental
class TestJoblocalhost:

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
