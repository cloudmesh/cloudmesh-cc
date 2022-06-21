###############################################################
# pytest -v --capture=no tests/test_queues.py
# pytest -v  tests/test_queues.py
# pytest -v --capture=no  tests/test_queues.py::Test_queue::<METHODNAME>
###############################################################
from cloudmesh.cc.queue import Queue, Queues
import os.path
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
import pytest
from pprint import pprint
import yaml

q = None

@pytest.mark.incremental
class TestConfig:

    def test_create(self):
        HEADING()
        global q
        Benchmark.Start()
        q = Queues(database='shelve')
        q.create(name='local')
        Benchmark.Stop()
        print(q.db.info())
        print ("HHHHH", q.db.data)
        # assert 'local' in q.db.data['queues']
        assert 'local' in q.db.data


    def test_add(self):
        HEADING()
        global q
        Benchmark.Start()
        q.add(name='local', job='job-1', command='echo hello world')
        q.add(name='local', job='job-2', command='echo is this working')
        q.add(name='local', job='job-3', command='echo I hope this is working')
        Benchmark.Stop()
        assert len(q.get("local")) == 3

    def test_remove(self):
        HEADING()
        global q
        Benchmark.Start()
        for i in range(3):
            name=f"queue-{i}"
            q.create(name=name)
            q.add(name=name, job=f"job-{i}", command=f"command-{i}")
        print('Current structure:')
        pprint(q.queues)
        print('Now removing 1 element')
        print(". . .")
        q.remove("queue-1")
        print('Current stricture: ')
        pprint(q.queues)
        Benchmark.Stop()
        print ("LLLL", q.queues)
        assert len(q.queues) == 3

    def test_list(self):
        HEADING()
        global q
        Benchmark.Start()
        for i in range(3):
            name=f"queue-{i}"
            q.create(name=name)
            q.add(name=name, job=i, command=f"command-{i}")
        print('The queues list() function prints out the following:')
        q.list()
        Benchmark.Stop()
        assert len(q.queues) == 4

    def test_run(self):
        HEADING()
        global q
        Benchmark.Start()
        for i in range(3):
            name=f"queue-{i}"
            q.create(name=name)

        for i in range(3):
            name = f"queue-{i}"

            q.add(name=name, job=1, command=f"pwd")
            q.add(name=name, job=2, command=f"hostname")
            q.add(name=name, job=3, command=f"uname")

        print('Current structure: ', q.queues)
        print('The list() function prints the following:')
        q.list()


        print(q)

        print(q.yaml)
        print(q.json)

        #for name, queue in q.queues.items():
        #    print (queue)
        Benchmark.Stop()
