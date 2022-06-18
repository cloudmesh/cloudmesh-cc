###############################################################
# pytest -v --capture=no tests/test_queue.py
# pytest -v  tests/test_queue.py
# pytest -v --capture=no  tests/test_queue.py::Test_queue::<METHODNAME>
###############################################################

from cloudmesh.cc.queue import Queue, Queues
import os.path
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
import pytest

@pytest.mark.incremental
class Test_Queue:

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

        q = Queue(name='queue 1')
        size = 10
        remove = int(size / 5)
        for x in range (0, size):
            job = f'job-{x}'
            command= f'command{x}'
            q.add(name=job, command=command)

        # result = q.list() should return a list of the items
        result = "temp"

        Benchmark.Start()
        for x in range(0, remove):
            job = f'job-{x}'
            q.remove(name=job)
        Benchmark.Stop()
        print("Before removal:")
        print()
        print(q.list())
        print()
        print("After removal")
        print()
        print(result)
        assert len(q.jobs) == size - remove

    def test_run(self):
        HEADING()
        q = Queue(name='queue 1')
        q.add(name='job1', command='cd')
        q.add(name='job2', command='echo hello world')
        q.add(name='job3', command='python3 ../cm/python-test/banner.py')

        Benchmark.Start()
        q.run(scheduler= "FIFO")
        Benchmark.Stop()
        assert q.jobs.get('job1') == 'cd'
        assert 'echo' in q.jobs.get('job2')
        assert 'banner' in q.jobs.get('job3')

    def test_list(self):
        HEADING()

        q = Queue(name= "queue 1")
        for x in range (0, 10):
            job = f'job-{x}'
            command= f'command{x}'
            q.add(name=job, command=command)
        Benchmark.Start()
        q.list()
        Benchmark.Stop()
        assert len(q.jobs) == 10

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc-queue")