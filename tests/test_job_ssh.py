###############################################################
# pytest -v --capture=no tests/test_job_ssh.py
# pytest -v  tests/test_job_ssh.py
# pytest -v --capture=no  tests/test_job_ssh.py::TestJobsSsh::<METHODNAME>
###############################################################
import os
import shutil
from pathlib import Path
from subprocess import STDOUT, check_output

import pytest
import time

from cloudmesh.cc.job.ssh.Job import Job
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Console
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables
from cloudmesh.vpn.vpn import Vpn

banner(Path(__file__).name, c = "#", color="RED")

variables = Variables()

name = "run"

if "host" not in variables:
    host = "rivanna.hpc.virginia.edu"
else:
    host = variables["host"]

username = variables["username"]

if username is None:
    Console.error("No username provided. Use cms set username=ComputingID")
    quit()

job = None

try:
    if not Vpn.enabled():
        raise Exception('vpn not enabled')
    check_output(f"ssh {username}@{host} hostname", stderr=STDOUT, timeout=6)
    login_success = True
except:  # noqa: E722
    login_success = False

run_job = f"run"
wait_job = f"run-killme"


@pytest.mark.skipif(not login_success, reason=f"host {username}@{host} not found or VPN not enabled")
@pytest.mark.incremental
class TestJobsSsh:

    def test_python(self):
        pyname = "hello-world"

        HEADING()
        Benchmark.Start()
        os.system(f"cp ./tests/{pyname}.py .")
        pyjob = Job(name=pyname, host=host, username=username, type="python")
        pyjob.sync()
        assert pyjob.exists(f"{pyname}.py")

        s, l = pyjob.run()
        # give it some time to complete
        time.sleep(5)
        print(l)
        # print(e)

        # log = pyjob.get_log()
        # print(log)
        Benchmark.Stop()


        # progress and status not supported yet
        # progress = pyjob.get_progress()
        # print("Progress:", progress)
        # status = pyjob.get_status(refresh=True)
        # print("Status:", status)
        assert l is not None
        assert s == 0
        # assert progress == 100
        # assert status == "done"
        assert pyjob.exists(f"{pyname}.py")


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

        Benchmark.Start()
        global job
        job = Job(name=f"run", host=host, username=username)
        job.sync()

        s, l = job.run()
        # give it some time to complete
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
        name = f"run"
        Benchmark.Start()
        correct = job.exists(f"{name}.sh")
        Benchmark.Stop()

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
        correct = job.exists(f"{name}.sh")
        Benchmark.Stop()

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
        time.sleep(2)
        banner(f"Job kill is done: {parent} {child}")

        Benchmark.Stop()

        child = job_kill.get_pid()
        status = job_kill.get_status()
        print("Status", status)
        Benchmark.Stop()
        ps = Shell.run(f'ssh {username}@{host} ps -eo pid').strip().replace(" ", "").splitlines()
        banner(f"{ps}")
        assert f"{parent}" not in ps
        assert f"{child}" not in ps
        assert status == "running"
