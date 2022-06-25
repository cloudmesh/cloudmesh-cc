###############################################################
# pytest -v --capture=no tests/test_graph.py
# pytest -v  tests/test_graph.py
# pytest -v --capture=no  tests/test_graph.py::Test_graph::<METHODNAME>
###############################################################
import os.path

import pytest

from cloudmesh.cc.workflow import Graph
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING

g = Graph()
g.sep = "_"

@pytest.mark.incremental
class Test_graph:


    def test_create(self):
        HEADING()
        Benchmark.Start()
        print("Edges:", g.nodes)
        print("Nodes:", g.edges)
        Benchmark.Stop()
        assert len(g.nodes) == 0
        assert len(g.edges) == 0

    def test_create(self):
        HEADING()
        Benchmark.Start()
        g.add_node("a", status="ready")
        g.add_node("b", **{"status": "ready"})
        print("Edges:", g.nodes)
        print("Nodes:", g.edges)
        Benchmark.Stop()
        assert len(g.nodes) == 2
        assert len(g.edges) == 0

    def test_edge(self):
        HEADING()
        Benchmark.Start()
        g.add_edge("a", "b", speed=50, temperature=10, status="ready")
        print("Edges:", g.nodes)
        print("Nodes:", g.edges)
        Benchmark.Stop()
        assert len(g.nodes) == 2
        assert len(g.edges) == 1

    def test_str(self):
        HEADING()
        Benchmark.Start()
        print (g)
        print (g.nodes.a["status"])
        print(g.nodes["a"]["status"])
        print(g.edges["a_b"]["status"])
        Benchmark.Stop()
        assert g.nodes.a["status"] == "ready"
        assert g.nodes["a"]["status"] == "ready"
        assert g.edges["a_b"]["status"] == "ready"
        print(g.edges.a_b["status"])

class rest:

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc-db")
