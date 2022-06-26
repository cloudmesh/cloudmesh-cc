###############################################################
# pytest -v --capture=no tests/test_workflow.py
# pytest -v  tests/test_workflow.py
# pytest -v --capture=no  tests/workflow.py::Test_queues::<METHODNAME>
###############################################################'
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

global w
"""
    This is a python file to test to make sure the workflow class works.
    It will draw upon the the test_queues file, because there is a file that
    was created with a bunch of jobs. 
"""

class Test_workflow:

    def test_set_up(self):
        """
        establishing a queues object, saving 2 queues to it, each with 10 jobs
        :return: no return
        """
        HEADING()
        global w
        Benchmark.Start()
        w = Workflow()

        login = {
            "localhost": {"user": "gregor", "host":"local"},
            "rivanna": {"user": "ggg", "host":"rivanna"},
            "pi": {"user": "gregor", "host":"red"},
        }

        n = 0

        user = login["localhost"]["user"]
        host = login["localhost"]["host"]

        w.add_job(name=f"start", kind="local", command='pwd', user=user, host=host)
        w.add_job(name=f"end", kind="local", command='pwd', user=user, host=host)

        for host, kind in [("localhost", "local"),
                           ("rivanna", "remote-slurm"),
                           ("pi", "ssh")]:
            print ("HOST:", host)
            user = login[host]["user"]
            host = login[host]["host"]
            w.add_job(name=f"job-{host}-{n}", kind=kind, command='pwd', user=user, host=host)
            n = n + 1
            w.add_job(name=f"job-{host}-{n}", kind=kind, command='ls', user=user, host=host)
            n = n + 1
            w.add_job(name=f"job-{host}-{n}", kind=kind, command='hostname', user=user, host=host)
            n = n + 1

            first = n - 3
            second = n -2
            third = n -1
            w.add_dependencies(f"job-{host}-{first},job-{host}-{second}")
            w.add_dependencies(f"job-{host}-{second},job-{host}-{third}")
            w.add_dependencies(f"job-{host}-{third},end")
            w.add_dependencies(f"start,job-{host}-{first}")

        Benchmark.Stop()
        print(len(w.jobs) == n)

    def test_show(self):
        HEADING()
        global w
        w.graph.save(filename="/tmp/test-dot.svg", colors="status", layout=nx.circular_layout, engine="dot")
        Shell.browser("/tmp/test-dot.svg")

class rest:


    def test_build(self):
        """
        This also tests the add nodes.
        :return:
        """
        HEADING()
        global w
        Benchmark.Start()
        w = Workflow(name= 'local',
                     dependencies=[2, 5, 3, 6, 9, 4],
                     database= 'yamldb',
                     filename="~/.cloudmesh/queue/queues")
        Benchmark.Stop()
        # print(w.nodes)
        # print(w.edges)
        assert len(w.nodes) == 6
        assert len(w.edges) == 5
        assert w.name == 'local'

    def test_get_node(self):
        HEADING()
        Benchmark.Start()
        node = w.get_node(name=9)
        Benchmark.Stop()
        print(node)
        assert node['name'] == 9

    def test_create_graph(self):
        HEADING()
        global w
        Benchmark.Start()
        w.create_graph()
        Benchmark.Stop()
        print(w.graph)
        assert len(w.graph) == 6

    def test_display(self):
        HEADING()
        global w
        Benchmark.Start()
        w.display()
        Benchmark.Stop()
        assert len(w.graph) == 6

    def test_run(self):
        HEADING()
        before = w.update_status()
        w.display_status()
        Benchmark.Start()
        w.run()
        Benchmark.Stop()
        after = w.update_status()
        w.display_status()
        assert w.counter == 6

    def test_status(self):
        HEADING()
        global w
        Benchmark.Start()
        w.update_status
        w.display_status
        Benchmark.Stop()
        assert w.get_status(name=2) == 'done'

class rest:

    def test_create_sorted_graph(self):
        HEADING()
        global w
        Benchmark.Start()
        w.create_sorted_graph()
        Benchmark.Stop()
        print(w.sorted_graph)
        assert len(w.sorted_graph) == 6