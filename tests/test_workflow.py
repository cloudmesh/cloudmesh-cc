# ##############################################################
# pytest -v -x --capture=no tests/test_workflow.py
# pytest -v  tests/test_workflow.py
# pytest -v --capture=no  tests/workflow.py::TestWorkflow::<METHODNAME>
# ##############################################################
import os.path
from pathlib import Path
from subprocess import STDOUT, check_output

import networkx as nx
import pytest

from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.variables import Variables
from cloudmesh.vpn.vpn import Vpn

banner(Path(__file__).name, c = "#", color="RED")

"""
    This is a python file to test to make sure the workflow class works.
    It will draw upon the the test_queues file, because there is a file that
    was created with a bunch of jobs. 
"""

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

w = None

try:
    if not Vpn.enabled():
        raise Exception('vpn not enabled')
    check_output(f"ssh {username}@{host} hostname", stderr=STDOUT, timeout=6)
    login_success = True
except:  # noqa: E722
    login_success = False


class TestWorkflow:

    def test_load_workflow(self):
        HEADING()
        global w
        Benchmark.Start()
        w = Workflow()
        w.load("tests/workflow.yaml")
        Benchmark.Stop()
        print(w.graph)

    def test_set_up(self):
        """
        establishing a queues object, saving 2 queues to it, each with 10 jobs
        :return: no return
        """
        HEADING()
        global w
        global username
        Benchmark.Start()
        w = Workflow()

        if os_is_windows():
            localuser = os.environ["USERNAME"]
        else:
            localuser = os.environ['USER']
        login = {
            "localhost": {"user": f"{localuser}", "host": "local"},
            "rivanna": {"user": f"{username}", "host": "rivanna.hpc.virginia.edu"},
            "pi": {"user": f"{localuser}", "host": "red"},
        }

        n = 0

        user = login["localhost"]["user"]
        host = login["localhost"]["host"]

        if os_is_windows():
            jobkind = "wsl"
        else:
            jobkind = "local"

        for script in ["start", "end"]:
            Shell.copy(f"./tests/workflow-sh/{script}.sh",".")
            assert os.path.isfile(f"./{script}.sh")
            w.add_job(name=script, kind=jobkind, user=user, host=host)


        for host, kind in [("localhost", jobkind),
                           # ("rivanna", "remote-slurm"),
                           ("rivanna", "ssh")]:
            print("HOST:", host)
            user = login[host]["user"]
            host = login[host]["host"]

            print(n)
            w.add_job(name=f"job-{host}-{n}", kind=kind, user=user, host=host)
            Shell.copy(f"./tests/workflow-sh/job-{host}-{n}.sh",".")
            # os.system(f"cp ./tests/workflow-sh/job-{host}-{n}.sh .")
            n = n + 1
            w.add_job(name=f"job-{host}-{n}", kind=kind, user=user, host=host)
            Shell.copy(f"./tests/workflow-sh/job-{host}-{n}.sh",".")
            n = n + 1
            w.add_job(name=f"job-{host}-{n}", kind=kind, user=user, host=host)
            Shell.copy(f"./tests/workflow-sh/job-{host}-{n}.sh",".")
            n = n + 1

            first = n - 3
            second = n - 2
            third = n - 1
            w.add_dependencies(f"job-{host}-{first},job-{host}-{second}")
            w.add_dependencies(f"job-{host}-{second},job-{host}-{third}")
            w.add_dependencies(f"job-{host}-{third},end")
            w.add_dependencies(f"start,job-{host}-{first}")


        Benchmark.Stop()
        print(len(w.jobs) == n)

    def test_show(self):
        HEADING()
        global w
        if os_is_windows():
            w.graph.save(filename="test-dot.svg", colors="status", layout=nx.circular_layout, engine="dot")
        else:
            w.graph.save(filename="/tmp/test-dot.svg", colors="status", layout=nx.circular_layout, engine="dot")
        # Shell.browser("/tmp/test-dot.svg")
        # assert os.path.exists("~/tmp/test-dot.svg") == True

    def test_get_node(self):
        HEADING()
        global w
        Benchmark.Start()
        s1 = w["start"]
        s2 = w.job("start")
        Benchmark.Stop()
        print(s1)
        assert s1 == s2

    def test_table(self):
        HEADING()
        global w
        Benchmark.Start()
        print(w.table)
        Benchmark.Stop()
        assert True

    def test_order(self):
        HEADING()
        global w
        Benchmark.Start()
        order = w.sequential_order()
        Benchmark.Stop()
        print(order)
        assert len(order) == len(w.jobs)

    @pytest.mark.skipif(not login_success, reason=f"host {username}@{host} not found or VPN not enabled")
    def test_run(self):
        HEADING()
        Benchmark.Start()
        w.run_topo()
        Benchmark.Stop()
        banner("Workflow")
        print(w.graph)

    def test_benchmark(self):
        HEADING()
        StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
