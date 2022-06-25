###############################################################
# pytest -v --capture=no tests/test_graph.py
# pytest -v  tests/test_graph.py
# pytest -v --capture=no  tests/test_graph.py::Test_graph::<METHODNAME>
###############################################################
import os.path

import pytest

from cloudmesh.cc.workflow import Graph
from cloudmesh.common.Benchmark import Benchmark, StopWatch
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

    def test_nodes(self):
        HEADING()
        Benchmark.Start()
        g.add_node("a", status="ready")
        g.add_node("b", **{"status": "ready"})
        print("Edges:", g.nodes)
        print("Nodes:", g.edges)
        Benchmark.Stop()
        assert len(g.nodes) == 2
        assert len(g.edges) == 0

    def test_edges(self):
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

    def test_dependency(self):
        HEADING()
        dependency = "c,d,e,f"
        Benchmark.Start()
        for n in dependency.split(","):
            g.add_node(n, status="ready")
        g.add_dependencies(dependency, edgedata={"status":"ready", "speed":"300"}, nodedata={"test": "one"})
        Benchmark.Stop()
        for n in dependency.split(","):
            assert g.nodes[n]["status"] == "ready"
            assert g.nodes[n]["test"] == "one"
        for name, e in g.edges.items():
            assert e["status"] == "ready"
        print(g)

    def test_dependency(self):
        HEADING()
        Benchmark.Start()
        g.show()
        Benchmark.Stop()

    def test_benchmark(self):
        HEADING()
        StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
