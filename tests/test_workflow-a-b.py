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


w = None


class TestWorkflowAB:

    def test_load_workflow(self):
        HEADING()
        global w
        Benchmark.Start()
        w = Workflow()
        w.load("tests/workflow-a-b.yaml")
        Benchmark.Stop()
        print(w.graph)



    def test_show(self):
        HEADING()
        global w
        w.graph.save(filename="workflow-a-b.svg",
                     colors="status",
                     layout=nx.circular_layout, engine="dot")

    def test_get_node(self):
        HEADING()
        global w
        Benchmark.Start()
        s1 = w["a"]
        s2 = w.job("a")
        Benchmark.Stop()
        print(s1)
        assert s1 == s2

    def test_table(self):
        HEADING()
        global w
        Benchmark.Start()
        table = str(w.table)
        print(table)
        Benchmark.Stop()
        assert "['a']" in table
        assert "test-a.sh" in table
        assert "[]" in table
        assert "test-b.sh" in table

    def test_order(self):
        HEADING()
        global w
        Benchmark.Start()
        order = w.sequential_order()
        Benchmark.Stop()
        print(order)
        assert len(order) == len(w.jobs)

    def test_benchmark(self):
        HEADING()
        StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
