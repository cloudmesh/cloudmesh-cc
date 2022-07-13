###############################################################
# pytest -v --capture=no tests/test_graph.py
# pytest -v  tests/test_graph.py
# pytest -v --capture=no  tests/test_graph.py::TestGraph::<METHODNAME>
###############################################################
import os.path

import networkx as nx
import pytest

from cloudmesh.cc.workflow import Graph
from cloudmesh.common.Benchmark import Benchmark, StopWatch
from cloudmesh.common.util import HEADING
from cloudmesh.common.Shell import Shell
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_mac

g = Graph()
g.sep = "_"


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

    def test_nodes(self):
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

    def test_str(self):
        HEADING()
        global g
        Benchmark.Start()
        print(g)
        output = str(g)
        print(g.nodes.a["status"])
        print(g.nodes["a"]["status"])
        print(g.edges["a_b"]["status"])
        Benchmark.Stop()
        assert g.nodes.a["status"] == "ready"
        assert g.nodes["a"]["status"] == "ready"
        assert g.edges["a_b"]["status"] == "ready"
        print(g.edges.a_b["status"])
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
        Shell.mkdir("dest")

        g.save(filename="dest/test-graphviz.svg", colors="status", layout=nx.circular_layout, engine="graphviz")
        g.save(filename="dest/test-dot.dot", colors="status", layout=nx.circular_layout, engine="dot")
        g.save(filename="dest/test-dot.svg", colors="status", layout=nx.circular_layout, engine="dot")

        # TODO: please fix shell cat for windows
        r = Shell.cat("dest/test-dot.dot")
        print(r)
        # TODO: please improve shell.browser so that when on linux we do svg gopen is used

        # TODO:
        # Shell.browser("dest/test-graphviz.svg")
        # Shell.browser("dest/test-dot.svg")

        # TODO: all this is part of Shell.browser

        if os_is_linux():
            Shell.run("gopen dest/test-graphviz.svg")
            Shell.run("gopen dest/test-dot.svg")
            # alternative is "chromium dest/test-dot.svg"
        elif os_is_mac():
            Shell.browser("dest/test-graphviz.svg")
            Shell.browser("dest/test-dot.svg")
        elif os_is_windows():
            Shell.browser("dest/test-graphviz.svg")
            # r = Shell.cat("test-dot.dot")
            # print(r)
            # TODO: please improve SHell.browser so it works on windows also
            cwd = os.getcwd()
            os.system(f'start chrome {cwd}\\dest\\test-dot.svg')
            os.system(f'start chrome {cwd}\\dest\\test-graphviz.svg')
            #Shell.browser("test-dot.svg", browser='chrome')
        Benchmark.Stop()

    def test_benchmark(self):
        HEADING()
        StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
