###############################################################
# pytest -v -x --capture=no tests/test_job_localhost.py
# pytest -v  tests/test_job_localhost.py
# pytest -v --capture=no  tests/test_job_localhost.py::TestJobLocalhost::<METHODNAME>
###############################################################

#
# program needs pip install pywin32 -U in requirements if on the OS is Windows
# TODO: check if pywin32 is the correct version
#

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import time

from cloudmesh.cc.job.localhost.Job import Job
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables

banner(Path(__file__).name, c = "#", color="RED")

if os_is_windows():
    Console.error("This test can not be run on windows")

variables = Variables()

host = "localhost"
if os_is_windows():
    username = os.environ["USERNAME"]
elif os_is_linux():
    username = os.system('whoami')
else:
    username = os.environ["USER"]

job = None

run_job = f"run"
wait_job = f"run-killme"


@pytest.mark.skipif(os_is_windows(), reason="Test can not be run on Windows")
@pytest.mark.incremental
class TestJobLocalhost:

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

        Benchmark.Start()
        name = f"run"
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
        job.sync()
        Benchmark.Stop()
        assert job.exists("run.sh")

    # potentially wrong
    def test_run_fast(self):
        HEADING()

        banner("create job")
        Benchmark.Start()
        global job
        job = Job(name=f"run", host=host, username=username)

        banner("create experiment")
        job.sync()

        banner("run job")
        s, l = job.run()
        print("State:", s)

        banner("check")

        finished = False
        log = None
        while not finished:
            log = job.get_log()
            if log is not None:
                progress = job.get_progress()
                finished = progress == 100
                print("Progress:", progress)
            if not finished:
                time.sleep(0.5)
        progress = job.get_progress()

        Benchmark.Stop()

        print("Progress:", progress)
        status = job.get_status(refresh=True)
        print("Status:", status)
        assert log is not None
        assert s == 0
        assert progress == 100
        assert status == "done"

    # will fail if previous test fails
    def test_exists_run(self):
        HEADING()
        global job
        name = f"run"
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
        jobWait.sync()
        s, l = jobWait.run()
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

        name = f"run"
        Benchmark.Start()
        wrong = job.exists(name)
        correct = job.exists(f"{name}.sh")
        Benchmark.Stop()

        assert not wrong
        assert correct

    def test_kill(self):
        """
        Creates a job from run-killme.sh, which includes wait of 1 hour
        Deletes this job AND it's children
        This way, it tests if the job or any of its children
        is found in the ps
        """
        HEADING()
        global username
        global host
        global wait_job

        Benchmark.Start()
        job_kill = Job(name=f"{wait_job}", host=host, username=username)
        banner("Clear the job log")
        job_kill.clear()
        banner("Sync the job to the experiment directory")
        job_kill.sync()

        banner("Run the job")
        job_kill.run()
        time.sleep(3)

        banner("Kill the Job")
        parent, child = job_kill.kill(period=2)
        banner(f"Job kill is done: {parent} {child}")

        Benchmark.Stop()

        child = job_kill.get_pid()
        status = job_kill.get_status()
        print("Status", status)
        Benchmark.Stop()
        ps = subprocess.check_output(f'ps -ax -o pid=', shell=True, text=True).strip()
        assert 'sleep 3600' not in ps

        banner(f"{ps}")
        assert f"{parent}" not in ps
        assert f"{child}" not in ps
        assert status == "running"
