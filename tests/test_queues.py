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



@pytest.mark.incremental
class TestConfig:

    def test_create(self):
        HEADING()
        Benchmark.Start()
        self.q = Queues(database='shelve')
        self.q.create(name='local')
        Benchmark.Stop()
        print ("HHHHH", self.q.db.data)
        assert 'local' in self.q.db.data['queues']

    def test_add(self):
        HEADING()
        self.q.create(name='local')
        Benchmark.Start()
        self.q.add(name='local', job='job-1', command='echo hello world')
        self.q.add(name='local', job='job-2', command='echo is this working')
        self.q.add(name='local', job='job-3', command='echo I hope this is working')
        Benchmark.Stop()
        assert len(self.q.queues) == 1

    def test_remove(self):
        HEADING()
        Benchmark.Start()
        q = Queues()
        for i in range(3):
            name=f"queue-{i}"
            self.q.create(name=name)
            self.q.add(name=name, job=i, command=f"command-{i}")
        print('Current structure: ', self.q.queues)
        print('Now removing 1 element')
        print(". . .")
        self.q.remove("queue-1")
        print('Current stricture: ', self.q.queues)
        Benchmark.Stop()
        assert len(self.q.queues) == 2

    def test_list(self):
        HEADING()
        Benchmark.Start()
        q = Queues(name='queues')
        for i in range(3):
            name=f"queue-{i}"
            self.q.create(name=name)
            self.q.add(name=name, job=i, command=f"command-{i}")
        print('The queues list() function prints out the following:')
        self.q.list()
        Benchmark.Stop()
        assert len(self.q.queues) == 3

    def test_run(self):
        HEADING()
        Benchmark.Start()
        q = Queues(name='queues')
        for i in range(3):
            name=f"queue-{i}"
            self.q.create(name=name)

        for i in range(3):
            name = f"queue-{i}"

            self.q.add(name=name, job=1, command=f"pwd")
            self.q.add(name=name, job=2, command=f"hostname")
            self.q.add(name=name, job=3, command=f"uname")

        print('Current structure: ', self.q.queues)
        print('The list() function prints the following:')
        self.q.list()


        for name, queue in self.q.queues.items():
            print (name)
            queue.run(scheduler='fifo')
        Benchmark.Stop()

        d = self.q.dict()
        pprint(d)
        print(yaml.dump(d))

        assert len(self.q.queues) == 3