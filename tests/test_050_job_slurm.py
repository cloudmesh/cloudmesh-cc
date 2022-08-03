###############################################################
# pytest -v --capture=no tests/test_050_job_slurm.py
# pytest -v  tests/test_050_job_slurm.py
# pytest -v --capture=no  tests/test_050_job_slurm.py::TestJobSlurm::<METHODNAME>
###############################################################
import os
import shutil
from pathlib import Path
from subprocess import STDOUT, check_output

import pytest
import time

from cloudmesh.cc.job.slurm.Job import Job
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Console
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables
from cloudmesh.vpn.vpn import Vpn
from cloudmesh.common.Shell import Shell

banner(Path(__file__).name, c = "#", color="RED")

cc_dir = Shell.map_filename("~/cm/cloudmesh-cc").path
os.chdir(cc_dir)
Shell.rmdir("dest")
Shell.mkdir("dest")
os.chdir("dest")

variables = Variables()

name = "run-slurm"


host = "rivanna.hpc.virginia.edu"
username = variables["username"]


if username is None:
    Console.error("No username provided. Use cms set username=ComputingID")
    quit()

job = None
job_id = None

try:
    if not Vpn.enabled():
        raise Exception('vpn not enabled')
    command = f"ssh {username}@{host} hostname"
    print (command)
    content = Shell.run(command, timeout=3)
    login_success = True
except Exception as e:  # noqa: E722
    print (e)
    login_success = False

run_job = f"run-slurm"
wait_job = f"wait-slurm"

@pytest.mark.incremental
class TestJobsSlurm:

    def test_create_run(self):
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
        name = f"run-slurm"
        job = Job(name=name, host=host, username=username)
        Benchmark.Stop()
        print(job)
        assert job.name == name
        assert job.host == host
        assert job.username == username

    @pytest.mark.skipif(not login_success, reason=f"host {username}@{host} not found or VPN not enabled")
    def test_sync(self):
        HEADING()
        global job

        Benchmark.Start()
        job.sync()
        Benchmark.Stop()
        assert job.exists("run-slurm.sh")

        # potentially wrong

    @pytest.mark.skipif(not login_success, reason=f"host {username}@{host} not found or VPN not enabled")
    def test_run_fast(self):
        HEADING()

        Benchmark.Start()
        global job
        global job_id
        job = Job(name=f"run-slurm", host=host, username=username)
        job.sync()

        s, job_id = job.run()
        # give it some time to complete
        # time.sleep(7)
        job.watch(period=0.5)

        print("State:", s)

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
    @pytest.mark.skipif(not login_success, reason=f"host {username}@{host} not found or VPN not enabled")
    def test_exists_run(self):
        HEADING()
        global job
        name = f"run-slurm"
        Benchmark.Start()
        correct = job.exists(f"{name}.sh")
        Benchmark.Stop()

        assert correct

    @pytest.mark.skipif(not login_success, reason=f"host {username}@{host} not found or VPN not enabled")
    def test_run_wait(self):
        HEADING()
        global run_job

        Benchmark.Start()
        jobWait = Job(name=f"{run_job}", host=host, username=username)
        jobWait.clear()
        jobWait.sync()
        # problem
        s, j = jobWait.run()
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

    @pytest.mark.skipif(not login_success, reason=f"host {username}@{host} not found or VPN not enabled")
    def test_exists_wait(self):
        HEADING()
        global job
        name = f"run-slurm"
        Benchmark.Start()
        correct = job.exists(f"{name}.sh")
        Benchmark.Stop()

        assert correct

    @pytest.mark.skipif(not login_success, reason=f"host {username}@{host} not found or VPN not enabled")
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
        global job_id

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
        r = job_kill.kill(period=2, job_id=job_id)
        assert job_id not in r
        banner(f"Job kill is done")

        Benchmark.Stop()

        # child = job_kill.get_pid()
        # status = job_kill.get_status()
        # print("Status", status)
        Benchmark.Stop()
        # ps = subprocess.check_output(f'ps -aux', shell=True, text=True).strip()
        # banner(f"{ps}")
        # assert 'sleep 3600' not in ps
        # assert f" {parent} " not in ps
        # assert f" {child} " not in ps
        # assert status == "running"
