# ##############################################################
# pytest -v -x --capture=no tests/test_workflow_local.py
# pytest -v  tests/test_workflow.py
# pytest -v --capture=no  tests/workflow.py::Test_queues::<METHODNAME>
# ##############################################################
import os.path
from pprint import pprint
import shelve
import pytest

from cloudmesh.cc.workflow import Workflow
from cloudmesh.cc.queue import Queues
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.Shell import Shell
import networkx as nx
from cloudmesh.common.variables import Variables
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
import shutil
from cloudmesh.common.util import banner

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

if "username" in variables:
    username = variables["username"]
else:
    username = os.path.basename(os.environ["HOME"])

global w


class Test_workflow:

    def test_load_workflow(self):
        HEADING()
        global w
        Benchmark.Start()
        w = Workflow()
        w.load(filename=path_expand('tests/workflow.yaml'), clear=True)
        Benchmark.Stop()
        print(w.graph)
        g = str(w.graph)
        assert w.filename == path_expand("~/.cloudmesh/workflow/workflow.yaml")
        assert "a-b:" in g
        assert "host: localhost" in g


    def test_reset_experiment_dir(self):
        os.system("rm -rf ~/experiment")
        exp = path_expand("~/experiment")
        shutil.rmtree(exp, ignore_errors=True)
        os.system('cp tests/workflow-sh/*.sh .')
        assert not os.path.isfile(exp)

class a:

    def test_set_up(self):
        """
        establishing a queues object, saving 2 queues to it, each with 10 jobs
        :return: no return
        """
        HEADING()
        global w
        global username
        Benchmark.Start()
        w = Workflow(filename=path_expand("tests/workflow.yaml"))

        login = {
            "localhost": {"user": "gregor", "host": "local"},
            "rivanna": {"user": f"{username}", "host": "rivanna.hpc.virginia.edu"},
            "pi": {"user": "gregor", "host": "red"},
        }

        n = 0

        user = login["localhost"]["user"]
        host = login["localhost"]["host"]

        w.add_job(name="start", kind="local", user=user, host=host)
        w.add_job(name="end", kind="local", user=user, host=host)

        for host, kind in [("localhost", "local"),
                           ("rivanna", "local")]:
            # ("rivanna", "ssh")

            print("HOST:", host)
            user = login[host]["user"]
            host = login[host]["host"]
            label = f'job-{host}-{n}'.replace('.hpc.virginia.edu', '')
            w.add_job(name=f"job-{host}-{n}", kind=kind, user=user, host=host)
            n = n + 1
            w.add_job(name=f"job-{host}-{n}", kind=kind, user=user, host=host)
            n = n + 1
            w.add_job(name=f"job-{host}-{n}", kind=kind, user=user, host=host)
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
            try:
                w.graph.save(filename="test-dot.svg", colors="status", layout=nx.circular_layout, engine="dot")
            except Exception as e:
                print(e.output)
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

    def test_run(self):
        HEADING()
        Benchmark.Start()
        w.run_parallel(show=True, period=1.0)
        Benchmark.Stop()
        banner("Workflow")
        print(w.graph)

    # def test_run(self):
    #     HEADING()
    #     Benchmark.Start()
    #     w.run(show=True)
    #     Benchmark.Stop()
    #     banner("Workflow")
    #     print(w.graph)

    # def test_remove_job(self):
    #     HEADING()
    #     global w
    #     Benchmark.Start()
    #     w.remove_job('job-local-1')


class todo:

    def test_benchmark(self):
        HEADING()
        # StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
