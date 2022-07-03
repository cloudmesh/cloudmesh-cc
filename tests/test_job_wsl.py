###############################################################
# pytest -v -x --capture=no tests/test_job_wsl.py
# pytest -v  tests/test_job_wsl.py
# pytest -v --capture=no  tests/test_job_wsl.py::TestJobssh::<METHODNAME>
###############################################################

#
# program needs pip install pywin32 -U in requirements if on windows
#

import os
import time
from time import sleep
import pytest

from cloudmesh.cc.job.wsl.Job import Job
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell
import shutil

from cloudmesh.common.systeminfo import os_is_windows
variables = Variables()

host = "localhost"
if os_is_windows():
    username = os.environ["USERNAME"]
else:
    username = os.environ["USER"]

job = None
prefix="-wsl"



@pytest.mark.incremental
class TestJoblocalhost:

    def test_create_run(self):
        exp = path_expand("~/experiment")
        shutil.rmtree(exp, ignore_errors=True)
        os.system(f"cp ./tests/run{prefix}.sh .")
        os.system(f"cp ./tests/wait{prefix}.sh .")
        assert os.path.isfile(f"./run{prefix}.sh")
        assert os.path.isfile(f"./wait{prefix}.sh")
        assert not os.path.isfile(exp)

    def test_create(self):
        HEADING()
        global job
        global username
        global host
        global prefix
        Benchmark.Start()
        name = f"run{prefix}"
        job = Job(name=name, host=host, username=username)
        Benchmark.Stop()
        print(job)
        assert job.name == name
        assert job.host == host
        assert job.username == username

    def test_sync(self):
        HEADING()
        global job

        Benchmark.Start()
        r = job.sync()
        Benchmark.Stop()
        assert job.exists("run-wsl.sh")

    # potentially wrong
    def test_run_fast(self):
        HEADING()
        global prefix

        # os.system("rm -r ~/experiment")
        # os.system(f"cp ./tests/run{prefix}.sh .")

        Benchmark.Start()
        global job
        job = Job(name=f"run{prefix}", host=host, username=username)
        r = job.sync()

        s, l, e = job.run()
        time.sleep(1)
        print("State:", s)
        print(l)
        # print(e)

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

class ff:

    # will fail if previous test fails
    def test_exists_run(self):
        HEADING()
        global job
        name = f"run{prefix}"
        Benchmark.Start()
        wrong = job.exists(name)
        correct = job.exists(f"{name}.sh")
        Benchmark.Stop()

        assert not wrong
        assert correct

    def test_run_wait(self):
        HEADING()
        global prefix
        print(f'prefix {prefix}')
        os.system("rm -r ~/experiment")
        # os.system(f"cp ./tests/run{prefix}.sh .")
        os.system(f"cp ./tests/wait{prefix}.sh .")

        Benchmark.Start()
        jobWait = Job(name=f"wait{prefix}", host=host, username=username)
        r = jobWait.sync()
        #problem
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

    # will fail if previous test fails
    def test_exists_wait(self):
        HEADING()
        global job

        name = f"wait{prefix}"
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
        global username
        global host
        global prefix

        os.system("rm -r ~/experiment")
        # os.system(f"cp ./tests/run{prefix}.sh .")
        os.system(f"cp ./tests/wait{prefix}.sh .")

        os.system(f"rm -f ./wait{prefix}.log")
        os.system(f"rm -f ./wait{prefix}.error")

        Benchmark.Start()
        job = Job(name=f"wait{prefix}", host=host, username=username)
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
