###############################################################
# pytest -v --capture=no tests/test_workflow_slurm.py
# pytest -v  tests/test_workflow_slurm.py
# pytest -v --capture=no  tests/test_workflow_slurm.py::TestWorkflowSlurm::<METHODNAME>
###############################################################
import os
from pathlib import Path
from subprocess import STDOUT, check_output

import networkx as nx
import pytest

from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Console
from cloudmesh.common.Shell import Shell
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.variables import Variables
from cloudmesh.vpn.vpn import Vpn

banner(Path(__file__).name, c = "#", color="RED")


variables = Variables()

name = "slurm"

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

w = None

@pytest.mark.incremental
class TestWorkflowSlurm:

    def test_load_slurm_workflow(self):
        HEADING()
        global w
        Benchmark.Start()
        w = Workflow()
        w.load("tests/workflow-slurm/slurm-workflow.yaml")
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

        user = login["rivanna"]["user"]
        host = login["rivanna"]["host"]

        jobkind = 'slurm'

        for script in ["start", "end"]:
            Shell.copy(f"./tests/workflow-slurm/{script}.sh", ".")
            assert os.path.isfile(f"./{script}.sh")
            w.add_job(name=script, kind=jobkind, user=user, host=host)

        for host, kind in [("rivanna", "slurm")]:
            print("HOST:", host)
            user = login[host]["user"]
            host = login[host]["host"]

            print(n)
            w.add_job(name=f"slurm", kind=kind, user=user, host=host)
            Shell.copy(f"./tests/workflow-slurm/slurm.sh", ".")
            # os.system(f"cp ./tests/workflow-slurm/job-{host}-{n}.sh .")
            n = n + 1

            w.add_dependencies(f"slurm,end")
            w.add_dependencies(f"start,slurm")


        Benchmark.Stop()
        print(len(w.jobs) == n)

    def test_show(self):
        HEADING()
        global w
        if os_is_windows():
            w.graph.save(filename="test-slurm.svg", colors="status", layout=nx.circular_layout, engine="dot")
        else:
            w.graph.save(filename="/tmp/test-slurm.svg", colors="status", layout=nx.circular_layout, engine="dot")
        # Shell.browser("/tmp/test-slurm.svg")
        # assert os.path.exists("~/tmp/test-slurm.svg") == True

    def test_get_node(self):
        HEADING()
        global w
        Benchmark.Start()
        s1 = w["slurm"]
        s2 = w.job("slurm")
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

    # def test_run(self):
    #     HEADING()
    #     Benchmark.Start()
    #     w.run_parallel()
    #     Benchmark.Stop()
    #     banner("Workflow")
    #     print(w.graph)
