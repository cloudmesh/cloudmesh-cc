###############################################################
# pytest -v --capture=no tests/test_workflow_slurm.py
# pytest -v  tests/test_workflow_slurm.py
# pytest -v --capture=no  tests/test_workflow_slurm.py::TestWorkflowSlurm::<METHODNAME>
###############################################################
import os
import shutil
import sys
import time
import io

import paramiko
import pexpect
from pexpect import popen_spawn

import pytest
from cloudmesh.cc.job.slurm.Job import Job

from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Console
from cloudmesh.common.variables import Variables
from cloudmesh.common.systeminfo import os_is_windows
import subprocess


variables = Variables()

name = "run-slurm"

if "host" not in variables:
    host = "rivanna.hpc.virginia.edu"
else:
    host = variables["host"]

username = variables["username"]

if username is None:
    Console.error("No username provided. Use cms set username=ComputingID")
    quit()

job = None
job_id = None
login_success = False

if not os_is_windows():
    try:
        command = f"ssh {username}@{host} hostname"
        #r = Shell.run(command)
        #print(r)
        #time.sleep(5)
        #login_success = "Could not resolve hostname" not in r
        ssh_new_key = "Are you sure you want to continue connecting"
        user_dir = os.path.expanduser('~/.ssh/id_rsa')

        paramiko_agent = paramiko.Agent()
        agent_keys = paramiko_agent.get_keys()

        client = paramiko.client.SSHClient()
        client.load_system_host_keys()
        mykey = paramiko.RSAKey.from_private_key_file(user_dir)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, look_for_keys=False, pkey=mykey)
        _stdin, _stdout, _stderr = client.exec_command('hostname')
        print(_stdout.read().decode())
        if 'not found in known_hosts' in _stdout.read().decode():
            Console.error('Please use ssh-keygen, ssh-agent, ssh-add, and ssh-copy-id')
            login_success = False
        else:
            login_success = True

    except Exception as e:  # noqa: E722
        if 'No such file or directory' and 'id_rsa' in str(e):
            Console.error('Please use ssh-keygen')
            quit()
        if 'Authentication failed' in str(e):
            Console.error('Please use ssh-copy-id')
            quit()
        print(e)
        pass

run_job = f"run-slurm"
wait_job = f"wait-slurm"


@pytest.mark.skipif(not login_success, reason=f"host {username}@{host} not found")
@pytest.mark.incremental
class TestWorkflowSlurm:

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
        name = f"run-slurm"
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
        assert job.exists("run-slurm.sh")

        # potentially wrong

    def test_run_fast(self):
        HEADING()

        Benchmark.Start()
        global job
        global job_id
        job = Job(name=f"run-slurm", host=host, username=username)
        job.sync()

        s, l, e, job_id = job.run()
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
        name = f"run-slurm"
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
        # problem
        s, l, e, j = jobWait.run()
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
        name = f"run-slurm"
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
        global prefix
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
        assert r.count('\n') == 1
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
