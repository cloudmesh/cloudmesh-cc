###############################################################
# pytest -v --capture=no tests/test_004_graph.py
# pytest -v  tests/test_004_graph.py
# pytest -v --capture=no  tests/test_004_graph.py::TestGraph::<METHODNAME>
###############################################################

from pathlib import Path

import networkx as nx
import pytest

from cloudmesh.cc.workflow import Graph
from cloudmesh.common.Benchmark import Benchmark, StopWatch
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
import os

banner(Path(__file__).name, c = "#", color="RED")

cc_path = Shell.map_filename("~/cm/cloudmesh-cc").path
os.chdir(cc_path)
Shell.rmdir("dest")
Shell.mkdir("dest")
os.chdir("dest")

g = Graph()


@pytest.mark.incremental
class TestGraph:

    def test_create(self):
        HEADING()
        global g
        Benchmark.Start()
        print("Edges:", g.nodes)
        print("Nodes:", g.edges)
        Benchmark.Stop()
        print(g)
        assert len(g.nodes) == 0
        assert len(g.edges) == 0

    def test_add_nodes(self):
        HEADING()
        global g
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
        global g
        Benchmark.Start()
        g.add_edge("a", "b", speed=50, temperature=10, status="ready")
        print(g)
        Benchmark.Stop()
        assert len(g.nodes) == 2
        assert len(g.edges) == 1

    def test_get_node(self):
        HEADING()
        global g
        Benchmark.Start()
        node1 = g.__getitem__('a')
        node2 = g.__getitem__('b')
        n1 = g['a']
        n2 = g['b']
        another_node1 = g.nodes['a']
        another_node2 = g.nodes['b']
        Benchmark.Stop()
        print('First Node: ', n1)
        print('Second Node: ', n2)
        assert node1 == n1 == another_node1
        assert node2 == n2 == another_node2

    def test_get_edge(self):
        HEADING()
        global g
        Benchmark.Start()
        e = g.edges['a-b']
        another_edge = g.edges['a-b']
        Benchmark.Stop()
        print('First Edge: ', e)
        assert e == another_edge

    def test_str(self):
        HEADING()
        global g
        Benchmark.Start()
        print(g)
        output = str(g)
        print(g.nodes.a["status"])
        print(g.nodes["a"]["status"])
        print(g.edges["a-b"]["status"])
        Benchmark.Stop()
        assert g.nodes.a["status"] == "ready"
        assert g.nodes["a"]["status"] == "ready"
        assert g.edges["a-b"]["status"] == "ready"
        print(g.edges["a-b"]["status"])
        assert ":" in output
        assert "ready" in output

    def test_dependency(self):
        HEADING()
        global g
        dependency = "c,d,e,f"
        print(dependency)
        Benchmark.Start()
        for n in dependency.split(","):
            g.add_node(n, status="ready")
        g.add_dependencies(dependency, edgedata={"status": "ready", "speed": "300"}, nodedata={"test": "one"})
        Benchmark.Stop()
        for n in dependency.split(","):
            assert g.nodes[n]["status"] == "ready"
            assert g.nodes[n]["test"] == "one"
        for name, e in g.edges.items():
            assert e["status"] == "ready"
        assert "f" in g.nodes.keys()
        print(g)

    def test_show(self):
        HEADING()
        global g
        g.nodes["a"]["status"] = "done"
        g.nodes["b"]["status"] = "failed"
        g.nodes["c"]["status"] = "running"

        g.add_dependencies("a,1,2,3,4,5,6,7,8,f", {"status": "done"})
        g.add_dependencies("b,c")

        g.add_color("status", ready="white", done="green")
        print(g)
        Benchmark.Start()
        print(g.colors)
        # g.show(colors="status", layout=nx.circular_layout, engine="networkx")

        g.save(filename="test-graphviz.svg", colors="status", layout=nx.circular_layout, engine="graphviz")
        g.save(filename="test-dot.dot", colors="status", layout=nx.circular_layout, engine="dot")
        g.save(filename="test-dot.svg", colors="status", layout=nx.circular_layout, engine="dot")

        r = Shell.cat("test-dot.dot")
        print(r)

        print ("display test-graphviz.svg")
        Shell.open('test-graphviz.svg')
        print ("display test-dot.svg")
        Shell.open('test-dot.svg')

        Benchmark.Stop()

    def test_clear(self):
        HEADING()
        g = Graph()
        assert g.nodes == {}
        assert g.edges == {}

        g.clear()
        print (g)
        assert g.nodes == {}
        assert g.edges == {}

    def test_load(self):
        HEADING()
        Shell.copy("../tests/workflows/workflow-a-b.yaml", "workflow-a-b.yaml")
        g = Graph()
        g.clear()
        banner("load workflow-a-b.yaml")
        g.load(filename="workflow-a-b.yaml")
        print (g)
        assert g.nodes != {}
        assert g.edges != {}
        assert "a-b" in g.edges
        assert "b-c" in g.edges

    def test_save(self):
        HEADING()
        cc_path = Shell.map_filename("~/cm/cloudmesh-cc/dest").path
        os.chdir(cc_path)
        g = Graph()
        g.clear()
        banner("load workflow-a-b.yaml")
        g.load(filename="workflow-a-b.yaml")
        # save
        Shell.rm("tmp-a.yaml")
        g.save_to_file("tmp-a.yaml")
        banner("load tmp-a.yaml")
        r = Shell.cat("tmp-a.yaml")
        print (r)
        assert g.nodes != {}
        assert g.edges != {}
        assert "a-b" in g.edges
        assert "b-c" in g.edges

    def test_save_full(self):
        HEADING()
        cc_path = Shell.map_filename("~/cm/cloudmesh-cc/dest").path
        os.chdir(cc_path)
        g = Graph()
        g.clear()
        banner("load workflow-a-b.yaml")
        g.load(filename="workflow-a-b.yaml")
        # save
        Shell.rm("tmp-a.yaml")
        g.save_to_file("tmp-a.yaml", exclude=None)
        banner("load tmp-a.yaml")
        r = Shell.cat("tmp-a.yaml")
        print (r)
        assert "parent" in r
        assert g.nodes != {}
        assert g.edges != {}
        assert "a-b" in g.edges
        assert "b-c" in g.edges


class a:
    def test_benchmark(self):
        HEADING()
        StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
