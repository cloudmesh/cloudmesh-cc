# ##############################################################
# pytest -v -x --capture=no tests/test_workflow_remote_ssh.py
# pytest -v  tests/test_workflow_remote_ssh.py
# pytest -v --capture=no  tests/test_workflow_remote_ssh.py::TestWorkflow::<METHODNAME>
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
from cloudmesh.common.util import path_expand

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
    command = f"ssh {username}@{host} hostname"
    print(command)
    content = Shell.run(command, timeout=3)
    login_success = True
except:  # noqa: E722
    login_success = False




def create_workflow():
    global w
    global username
    w = Workflow(filename=path_expand("tests/workflow.yaml"), clear=True)

    if os_is_windows():
        localuser = os.environ["USERNAME"]
    else:
        try:
            localuser = os.environ['USER']
        except:
            # docker image does not have user variable. so just do basename of home
            localuser = os.system('basename $HOME')
    login = {
        "localhost": {"user": f"{localuser}", "host": "local"},
        "rivanna": {"user": f"{username}", "host": "rivanna.hpc.virginia.edu"},
        "pi": {"user": f"{localuser}", "host": "red"},
    }

    n = 0

    user = login["localhost"]["user"]
    host = login["localhost"]["host"]

    jobkind="local"

    w.add_job(name="start", kind=jobkind, user=user, host=host)
    w.add_job(name="end", kind=jobkind, user=user, host=host)

    for host, kind in [("localhost", jobkind),
                       ("rivanna", "ssh")]:

        # ("rivanna", "ssh")

        print("HOST:", host)
        user = login[host]["user"]
        host = login[host]["host"]
        # label = f'job-{host}-{n}'.replace('.hpc.virginia.edu', '')

        label = "'debug={cm.debug}\\nhome={os.HOME}\\n{name}\\n{now.%m/%d/%Y, %H:%M:%S}\\nprogress={progress}'"

        w.add_job(name=f"job-{host}-{n}", label=label,  kind=kind, user=user, host=host)
        n = n + 1
        w.add_job(name=f"job-{host}-{n}", label=label, kind=kind, user=user, host=host)
        n = n + 1
        w.add_job(name=f"job-{host}-{n}", label=label, kind=kind, user=user, host=host)
        n = n + 1

        first = n - 3
        second = n - 2
        third = n - 1
        w.add_dependencies(f"job-{host}-{first},job-{host}-{second}")
        w.add_dependencies(f"job-{host}-{second},job-{host}-{third}")
        w.add_dependencies(f"job-{host}-{third},end")
        w.add_dependencies(f"start,job-{host}-{first}")

    print(len(w.jobs) == n)
    g = str(w.graph)
    print(g)
    assert "name: start" in g
    assert "start-job-rivanna.hpc.virginia.edu-3:" in g
    return w



class TestWorkflowSsh:

    # def test_load_workflow(self):
    #     HEADING()
    #     global w
    #     Benchmark.Start()
    #     w = Workflow()
    #     w.load(filename=path_expand('tests/workflow.yaml'), clear=True)
    #     Benchmark.Stop()
    #     g = str(w.graph)
    #     print(g)
    #     assert w.filename == path_expand("~/.cloudmesh/workflow/workflow.yaml")
    #     assert "start" in g
    #     assert "host: local" in g
    #     print(w.graph)

    def test_experiment_setup(self):

        Shell.mkdir("experiment")
        # copy all files needed into experiment
        # run all other tests in ./experiment_ssh
        # os.chdir("./experiment_ssh")
        # then run all test there

    def test_create_workflow(self):
        HEADING()
        global w
        Benchmark.Start()
        w = create_workflow()
        Benchmark.Stop()
        g = str(w.graph)
        print(g)
        assert "start" in g
        assert "host: local" in g
        print(w.graph)


    def test_show(self):
        HEADING()
        global w
        w.graph.save(filename="ssh.svg", colors="status",  engine="dot")
        Shell.open("ssh.svg")
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
        print(w.table2(with_label=True))
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
        input()

    @pytest.mark.skipif(not login_success, reason=f"host {username}@{host} not found or VPN not enabled")
    def test_run_tooo(self):
        HEADING()
        Benchmark.Start()
        w.run_topo(show=True, filename="topo.svg")
        Benchmark.Stop()
        banner("Workflow")
        print(w.graph)

    # @pytest.mark.skipif(not login_success, reason=f"host {username}@{host} not found or VPN not enabled")
    # def test_run_parallel(self):
    #     HEADING()
    #     Benchmark.Start()
    #     w.run_parallel(show=True, filename="parallel.svg")
    #     Benchmark.Stop()
    #     banner("Workflow")
    #     print(w.graph)

    def test_benchmark(self):
        HEADING()
        StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
