# ##############################################################
# pytest -v -x --capture=no tests/test_030_workflow-a-b.py
# pytest -v  tests/test_030_workflow.py
# pytest -v --capture=no  tests/test_030_workflow.py::TestWorkflow::<METHODNAME>
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
from cloudmesh.common.util import readfile
from utilities import create_dest

create_dest()

banner(Path(__file__).name, c = "#", color="RED")

variables = Variables()

name = "run"

variables["user"] = Shell.user()
variables["host"] = Shell.host()

print(variables["host"])


w = None
w1 = None


class TestWorkflowAB:

    def test_load_workflow(self):
        HEADING()
        global w
        Benchmark.Start()
        w = Workflow()
        w.load("../workflows/workflow-a-b.yaml")
        Benchmark.Stop()
        print(w.graph)
        print(w.table)


class d:
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


        # assert "['a']" in table
        # assert "test-a.sh" in table
        # assert "[]" in table
        # assert "test-b.sh" in table

class h:
    def test_table_2(self):
        HEADING()
        global w
        Benchmark.Start()
        table = str(w.table2(with_label=True))
        print(table)
        Benchmark.Stop()
        assert "['a']" in table
        assert "test-a.sh" in table
        assert "[]" in table
        assert "test-b.sh" in table

    def test_show(self):
        HEADING()
        global w

        w.graph.save(filename="workflow-a-b.svg", colors="status", engine="dot")
        #Shell.browser("/tmp/workflow-a-b.svg")
        os.system('open workflow-a-b.svg')
        #os.path.exists("/tmp/test-dot.svg")

    def test_order(self):
        HEADING()
        global w
        Benchmark.Start()
        order = w.sequential_order()
        Benchmark.Stop()
        print(order)
        assert len(order) == len(w.jobs)

    def test_save(self):
        HEADING()
        global w
        dest = "workflow-a-b.yaml"
        Benchmark.Start()
        w.save(filename=dest)
        Benchmark.Stop()
        content = readfile(dest)
        print (content)

    def test_save_with_state(self):
        HEADING()
        global w
        dest = "workflow-a-b-state.yaml"
        Benchmark.Start()
        w.save_with_state(filename=dest)
        Benchmark.Stop()
        content = readfile(dest)
        banner("read with state")
        print(content)

    def test_read_with_state(self):
        HEADING()
        global w
        dest = "workflow-a-b-state.yaml"
        Benchmark.Start()
        d = w.save_with_state(filename=dest,stdout=True).strip()
        w.load_with_state(filename=dest)
        Benchmark.Stop()
        content = readfile(dest).strip()
        banner("load with state")
        print(content)
        assert d == content

    def test_new_workflow(self):
        HEADING()
        dest = "workflow-a-b-state.yaml"
        w = Workflow()
        w.load_with_state(filename=dest)
        content = readfile(dest).strip()
        banner("load from clear workflow with state")
        print(content)
        # d = w.save_with_state(filename=dest,stdout=True).strip()
        # assert d == content

class a:
    def test_benchmark(self):
        HEADING()
        StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
