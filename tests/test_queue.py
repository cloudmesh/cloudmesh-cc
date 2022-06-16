from cloudmesh.cc.queue import Queue, Queues
import os.path
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
import pytest

class TestConfig:

    def test_create(self):
        HEADING()
        Benchmark.Start()
        q = Queue(name='queue 1')
        print(q.name)
        print(q.jobs)
        Benchmark.Stop()
        assert q.name == 'queue 1'

    def test_add(self):
        HEADING()
        Benchmark.Start()
        q = Queue(name='queue 1')

        for x in range (0, 10):
            job = f'job-{x}'
            command= f'command{x}'
            q.add(name=job, command=command)
        q.list()
        Benchmark.Stop()
        assert len(q.jobs) == 10

    def test_remove(self):
        HEADING()
        Benchmark.Start()
        q = Queue(name='queue 1')
        for x in range (0, 10):
            job = f'job-{x}'
            command= f'command{x}'
            q.add(name=job, command=command)
        print("Before removal:" )
        print()
        q.list()
        print()

        for x in range(0, 2):
            job = f'job-{x}'
            q.remove(name=job)

        print("After removal")
        print()
        q.list()

        assert len(q.jobs) == 8

    def test_run(self):
        HEADING()
        Benchmark.Start()
        q = Queue(name='queue 1')
        q.add(name='job1', command='cd')
        q.add(name='job2', command='echo hello world')
        q.add(name='job3', command='python3 /Users/jacksonmiskill/cm/python-test/banner.py')

        q.run(scheduler= "FIFO")
        Benchmark.Stop()
        assert q.jobs.get('job1') == 'cd'

    def test_list(self):
        HEADING()
        Benchmark.Start()
        q = Queue(name= "queue 1")
        for x in range (0, 10):
            job = f'job-{x}'
            command= f'command{x}'
            q.add(name=job, command=command)
        q.list()
        Benchmark.Stop()
        assert len(q.jobs) == 10
