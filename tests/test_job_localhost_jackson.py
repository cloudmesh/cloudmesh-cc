###############################################################
# pytest -v --capture=no tests/test_job_localhost_jackson.py
# pytest -v  tests/test_job_ssh.py
# pytest -v --capture=no  tests/test_job_ssh.py::TestJobssh::<METHODNAME>
###############################################################
import os

import pytest

from cloudmesh.cc.job.localhost.JacksonJob import Job
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import path_expand
variables = Variables()

name = "run"

if "host" not in variables:
    host = "localhost"
else:
    host = variables["host"]

username = variables["username"]

job = None


@pytest.mark.incremental
class TestJoblocalhost:

    def test_create_run(self):
        os.system("cp ./tests/run.sh .")
        os.system("cp ./tests/wait.sh .")
        assert os.path.isfile("./run.sh")
        assert os.path.isfile("./wait.sh")

    def test_create(self):
        HEADING()
        global job
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

        Benchmark.Start()
        r = job.sync("./tests/run.sh")

        Benchmark.Stop()
        # successful exit status
        assert r == 0

    def test_run(self):
        HEADING()
        global job

        Benchmark.Start()
        s, l, e = job.run()
        print("State:", s)
        # print(l)
        # print(e)

        Benchmark.Stop()

        assert s == 0

    def test_progress_status(self):
        HEADING()
        global job

        Benchmark.Start()
        job.get_log()
        progress = job.get_progress()
        print("Progress:", progress)
        status = job.get_status()
        print("Status:", status)
        Benchmark.Stop()

        assert progress == 100
        assert status == "done"

    def test_exists(self):
        HEADING()
        global job

        Benchmark.Start()
        wrong = job.exists(name)
        correct = job.exists(f"{name}.sh")
        Benchmark.Stop()

        assert not wrong
        assert correct

    def test_watch(self):
        HEADING()
        global job
        global username
        global host
        global name
        Benchmark.Start()
        os.remove(path_expand(f"{job.directory}/run.log"))
        os.remove(path_expand(f"{job.directory}/run.err"))
        job = Job(name=name, host=host, username=username)
        r = job.sync("./tests/run.sh")
        job.run()
        job.watch(period=1)
        status = job.get_status()
        Benchmark.Stop()
        assert status == "done"

    def test_kill(self):
        HEADING()
        global job
        global username
        global host
        global name

        name = "wait"
        Benchmark.Start()
        os.remove(path_expand(f"{job.directory}/{name}.log")) if os.path.exists(path_expand(f"{job.directory}/{name}.log")) else None
        os.remove(path_expand(f"{job.directory}/{name}.err")) if os.path.exists(path_expand(f"{job.directory}/{name}.err")) else None
        job = Job(name=name, host=host, username=username)
        r = job.sync(f"./tests/{name}.sh")
        pid = job.get_pid(refresh=True)
        job.kill()
        status = job.get_status()
        print ("Status", status)
        Benchmark.Stop()
        # assert status == "done"
        # check with ps if pid is running
