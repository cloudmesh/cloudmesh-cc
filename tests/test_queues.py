from cloudmesh.cc.queue import Queue, Queues
import os.path
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
import pytest

class TestConfig:

    def test_create(self):
        HEADING()
        Benchmark.Start()
        q = Queues(name='queues structure')
        print('Structure name: ', q.name)
        print('Current structure:', q.queues)
        print('Current file: ', q.db)
        Benchmark.Stop()
        assert q.name == 'queues structure'

    def test_add(self):
        HEADING()
        Benchmark.Start()
        q = Queues(name='queues structure')
        q1 = Queue(name='queue 1')
        q2 = Queue(name='queue 2')
        q3 = Queue(name='queue 3')
        q.add(q1)
        q.add(q2)
        q.add(q3)
        print('Current structure: ', q.queues)
        Benchmark.Stop()
        assert len(q.queues) == 3

    def test_remove(self):
        HEADING()
        Benchmark.Start()
        q = Queues(name='queues structure')
        q1 = Queue(name='queue 1')
        q2 = Queue(name='queue 2')
        q3 = Queue(name='queue 3')
        q.add(q1)
        q.add(q2)
        q.add(q3)
        print('Current structure: ', q.queues)
        print('Now removing 1 element')
        print(". . .")
        q.remove(q1.name)
        print('Current stricture: ', q.queues)
        Benchmark.Stop()
        assert len(q.queues) == 2

    def test_list(self):
        HEADING()
        Benchmark.Start()
        q = Queues(name='queues structure')
        q1 = Queue(name='queue 1')
        q2 = Queue(name='queue 2')
        q3 = Queue(name='queue 3')
        q.add(q1)
        q.add(q2)
        q.add(q3)
        print('The queues list() function prints out the following:')
        q.list()
        Benchmark.Stop()
        assert len(q.queues) == 3

    def test_run(self):
        HEADING()
        Benchmark.Start()
        q = Queues(name='queues structure')

        q1 = Queue(name='queue 1')
        q1.add(name='job1', command='echo this is queue 1')
        q1.add(name='job2', command='cd')
        q1.add(name='job3', command='python /Users/jacksonmiskill/cm/python-test/barchart.py ')

        q2 = Queue(name='queue 2')
        q2.add(name='job1', command='echo this is queue 2')
        q2.add(name='job2', command='cd ~')
        q2.add(name='job3', command='ls')

        q3 = Queue(name='queue 3')
        q3.add(name='job1', command='echo this is queue 3')
        q3.add(name='job2', command='cd ~')
        q3.add(name='job3', command='python /Users/jacksonmiskill/cm/PythonPractice/youmadeit.py')

        q.add(q1)
        q.add(q2)
        q.add(q3)

        print('Current structure: ', q.queues)
        print('The list() function prints the following:')
        q.list()

        q.run(scheduler='fifo')
        Benchmark.Stop()
        assert len(q.queues) == 3


    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc-queues")





