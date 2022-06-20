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
        q = Queues(name='queues')
        print('Structure name: ', q.name)
        print('Current structure:', q.queues)
        print('Current file: ', q.db)
        Benchmark.Stop()
        assert q.name == 'queues'

    def test_add(self):
        HEADING()
        Benchmark.Start()
        q = Queues(name='queues')
        for i in range(3):
            name=f"queue-{i}"
            q.create(name=name)
            q.add(name=name, job=i, command=f"command-{i}")
        print('Current structure: ', q.queues)
        Benchmark.Stop()
        assert len(q.queues) == 3

    def test_remove(self):
        HEADING()
        Benchmark.Start()
        q = Queues(name='queues')
        for i in range(3):
            name=f"queue-{i}"
            q.create(name=name)
            q.add(name=name, job=i, command=f"command-{i}")
        print('Current structure: ', q.queues)
        print('Now removing 1 element')
        print(". . .")
        q.remove("queue-1")
        print('Current stricture: ', q.queues)
        Benchmark.Stop()
        assert len(q.queues) == 2

    def test_list(self):
        HEADING()
        Benchmark.Start()
        q = Queues(name='queues')
        for i in range(3):
            name=f"queue-{i}"
            q.create(name=name)
            q.add(name=name, job=i, command=f"command-{i}")
        print('The queues list() function prints out the following:')
        q.list()
        Benchmark.Stop()
        assert len(q.queues) == 3

    def test_run(self):
        HEADING()
        Benchmark.Start()
        q = Queues(name='queues')
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


        for name, queue in q.queues.items():
            print (name)
            queue.run(scheduler='fifo')
        Benchmark.Stop()

        d = q.dict()
        pprint(d)
        print(yaml.dump(d))

        assert len(q.queues) == 3



class a:


    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc-queues")





