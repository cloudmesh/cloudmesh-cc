###############################################################
# pytest -v -x --capture=no tests/test_010_job_localhost.py
# pytest -v  tests/test_010_job_localhost.py
# pytest -v --capture=no  tests/test_010_job_localhost.py::TestJobLocalhost::<METHODNAME>
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
from cloudmesh.common.Shell import Shell
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import readfile
from utilities import create_dest

create_dest()

banner(Path(__file__).name, c = "#", color="RED")


variables = Variables()

host = "localhost"
username = Shell.sys_user()

job = None

run_job = f"run"
wait_job = f"run-killme"


# @pytest.mark.skipif(os_is_windows(), reason="Test can not be run on Windows")
@pytest.mark.incremental
class TestJobLocalhost:

    def test_create_run(self):
        HEADING()
        os.system("rm -r ~/experiment")
        exp = path_expand("~/experiment")
        shutil.rmtree(exp, ignore_errors=True)
        for script in [run_job, wait_job]:
            os.system(f"cp ../tests/scripts/{script}.sh .")
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
        s = job.run()
        job.watch(period=0.5)
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
        s = jobWait.run()
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
        ps = subprocess.check_output('ps', shell=True, text=True)
        if not os_is_windows():
            ps = subprocess.check_output(f'ps -ax', shell=True, text=True).strip()
            assert 'sleep 3600' not in ps

        banner(f"{ps}")
        assert f"{parent}" not in ps
        assert f"{child}" not in ps
        assert status == "running"

    def test_create_exec(self):
        HEADING()
        global job
        global username
        global host

        Benchmark.Start()
        name = f"run"

        job = Job(name="os", host=host, username=username, exec="echo hallo")
        print(job)
        content = readfile("os.sh")
        assert "echo hallo" in content
        assert job.name == "os"
        assert job.host == host
        assert job.username == username


        job = Job(name="python", host=host, username=username, exec="run.py")
        print(job)
        content = readfile("python.sh")
        assert "run.py" in content
        assert job.name == "python"
        assert job.host == host
        assert job.username == username

        job = Job(name="notebook", host=host, username=username, exec="run.ipynb")
        print(job)
        content = readfile("notebook.sh")
        assert job.name == "notebook"
        assert job.host == host
        assert job.username == username

        job = Job(name="run-other", host=host, username=username, exec="other.sh")
        print(job)
        content = readfile("run-other.sh")
        assert "other.sh" in content
        assert job.name == "run-other"
        assert job.host == host
        assert job.username == username

        Benchmark.Stop()
