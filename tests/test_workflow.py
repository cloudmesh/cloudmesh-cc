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

global w
global q
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
        global q
        Benchmark.Start()
        q = Queues(filename="~/.cloudmesh/queue/queues", database='yamldb')
        q.create(name='local')
        q.create(name='rivanna')
        q.create(name='raspberry')

        # adding jobs to 'local' the commands are semi randomized because I wanted them to work on any OS
        q.add(name='local', job=1, command='pwd')
        q.add(name='local', job=2, command='ls')
        q.add(name='local', job=3, command='hostname')
        q.add(name='local', job=4, command='pwd')
        q.add(name='local', job=5, command='hostname')
        q.add(name='local', job=6, command='ls')
        q.add(name='local', job=7, command='hostname')
        q.add(name='local', job=8, command='pwd')
        q.add(name='local', job=9, command='hostname')
        q.add(name='local', job=10, command='ls')

        # adding jobs to 'rivanna' the commands are semi randomized because I wanted them to work on any OS
        q.add(name='rivanna', job=1, command='pwd')
        q.add(name='rivanna', job=2, command='ls')
        q.add(name='rivanna', job=3, command='hostname')
        q.add(name='rivanna', job=4, command='pwd')
        q.add(name='rivanna', job=5, command='hostname')
        q.add(name='rivanna', job=6, command='ls')
        q.add(name='rivanna', job=7, command='hostname')
        q.add(name='rivanna', job=8, command='pwd')
        q.add(name='rivanna', job=9, command='hostname')
        q.add(name='rivanna', job=10, command='ls')

        # adding jobs to 'raspberry' the commands are semi randomized because I wanted them to work on any OS
        q.add(name='raspberry', job=1, command='pwd')
        q.add(name='raspberry', job=2, command='ls')
        q.add(name='raspberry', job=3, command='hostname')
        q.add(name='raspberry', job=4, command='pwd')
        q.add(name='raspberry', job=5, command='hostname')
        q.add(name='raspberry', job=6, command='ls')
        q.add(name='raspberry', job=7, command='hostname')
        q.add(name='raspberry', job=8, command='pwd')
        q.add(name='raspberry', job=9, command='hostname')
        q.add(name='raspberry', job=10, command='ls')
        Benchmark.Stop()
        print(q)
        assert len(q.queues) == 3


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

    def test_status(self):
        HEADING()
        global w
        Benchmark.Start()
        sta = {}
        for job in w.nodes:
            name = job['name']
            s = w.status(job)
            sta[name] = s
        print(sta)
        Benchmark.Stop()
        assert sta[2] == 'ready'

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
        Benchmark.Start()
        w.run()
        Benchmark.Stop()
        assert w.counter == 6

class rest:

    def test_create_sorted_graph(self):
        HEADING()
        global w
        Benchmark.Start()
        w.create_sorted_graph()
        Benchmark.Stop()
        print(w.sorted_graph)
        assert len(w.sorted_graph) == 6


