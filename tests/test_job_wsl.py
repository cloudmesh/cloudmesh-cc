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

import subprocess
from cloudmesh.cc.job.wsl.Job import Job
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import banner
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

run_job = f"run{prefix}"
wait_job = f"wait{prefix}"




@pytest.mark.incremental
class TestJoblocalhost:


    def test_create_run(self):
        os.system("rm -r ~/experiment")
        exp = path_expand("~/experiment")
        shutil.rmtree(exp, ignore_errors=True)
        for script in [run_job, wait_job]:
            os.system(f"cp ./tests/{script}.sh .")
            assert os.path.isfile(f"./{script}.sh")
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
        # give it time to complete
        time.sleep(5)
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
        global run_job

        Benchmark.Start()
        jobWait = Job(name=f"{run_job}", host=host, username=username)
        jobWait.clear()
        r = jobWait.sync()
        #problem
        s, l, e = jobWait.run()
        jobWait.watch(period=0.5)
        log = jobWait.get_log()
        progress = jobWait.get_progress()
        print("Progress:", progress)
        status = jobWait.get_status(refresh=True)
        print("Status:", status, s, progress)
        assert log is not None
        assert s == 0
        assert progress == 100
        assert status == "done"

        Benchmark.Stop()

    # will fail if previous test fails
    def test_exists_wait(self):
        HEADING()
        global job

        name = f"run{prefix}"
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
        global wait_job

        Benchmark.Start()
        job_kill = Job(name=f"{wait_job}", host=host, username=username)
        banner("Cear the job log")
        job_kill.clear()
        banner("Sync the job to the experiment directory")
        r = job_kill.sync()

        banner("Run the job")
        s, l, e = job_kill.run()
        time.sleep(3)

        banner("Kill the Job")
        parent, child = job_kill.kill(period=2)
        banner(f"Job kill is done: {parent} {child}")

        Benchmark.Stop()

        child = job_kill.get_pid()
        status = job_kill.get_status()
        print("Status", status)
        Benchmark.Stop()
        ps = subprocess.check_output(f'wsl ps -aux', shell=True, text=True).strip()
        banner(f"{ps}")
        assert 'sleep 3600' not in ps
        assert f" {parent} " not in ps
        assert f" {child} " not in ps
        assert status == "running"

