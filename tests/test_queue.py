###############################################################
# pytest -v --capture=no tests/test_queue.py
# pytest -v  tests/test_queue.py
# pytest -v --capture=no  tests/test_queue.py::Test_queue::<METHODNAME>
###############################################################

import pytest

from cloudmesh.cc.queue import Queue
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING

q = None


@pytest.mark.incremental
class Test_Queue:

    def test_create(self):
        HEADING()
        global q
        Benchmark.Start()
        q = Queue(name='queue-1')
        print(q)
        Benchmark.Stop()
        assert q.name == 'queue-1'

    def test_add(self):
        HEADING()
        global q
        Benchmark.Start()
        for x in range(0, 10):
            job = f'job-{x}'
            command = f'command{x}'
            q.add(name=job, command=command)
        print('The jobs: ')
        q.list()
        Benchmark.Stop()
        assert len(q.jobs) == 10

    def test_remove(self):
        HEADING()
        global q
        size = len(q.jobs)
        remove = int(size / 2)
        # result = q.list() should return a list of the items
        result = "temp"
        Benchmark.Start()
        print('Before removal')
        q.list()
        for x in range(0, remove):
            job = f'job-{x}'
            q.remove(name=job)
        print('After removal')
        q.list()
        Benchmark.Stop()
        assert len(q.jobs) == size - remove

    def test_run(self):
        HEADING()
        q = Queue(name='queue-1')
        q.add(name='job1', command='pwd')
        q.add(name='job2', command='echo hello world')
        q.add(name='job3', command='hostname')

        print(q)

        Benchmark.Start()
        #q.run(scheduler="FIFO")
        Benchmark.Stop()
        print("job object:", q.jobs['job1'])
        assert q.jobs.get('job1').command == 'pwd'
        assert 'echo' in q.jobs.get('job2').command
        assert 'hostname' in q.jobs.get('job3').command

    def test_list(self):
        HEADING()
        global q
        print("Testing to see if the q.list() method works for queue not queues")
        Benchmark.Start()
        q.list()
        Benchmark.Stop()
        assert len(q.jobs) == 5

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc-queue")
