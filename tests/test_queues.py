###############################################################
# pytest -v --capture=no tests/test_queues.py
# pytest -v  tests/test_queues.py
# pytest -v --capture=no  tests/test_queues.py::Test_queues::<METHODNAME>
###############################################################
import os.path
from pprint import pprint

import pytest

from cloudmesh.cc.queue import Queues
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING

kind = "yamldb"
kind = "shelve"
q = None

@pytest.mark.incremental
class Test_queues:

    def test_create(self):
        HEADING()
        global q
        Benchmark.Start()
        q = Queues(database=kind)
        # q.create(name='local')
        Benchmark.Stop()
        # print(q.info())
        #assert 'local' in q.queues

class a:
    def test_filename(self):
        s1 = "~/.cloudmesh/queue/queuetest1"
        s2 = "~/.cloudmesh/queue/queuetest2.db"
        s3 = "~/.cloudmesh/queue/queuetest3.dat"
        q1 = Queues(filename=s1)
        q1.close()
        # q2 = Queues(filename=s2)
        q3 = Queues(filename=s3)
        q3.close()
        assert os.path.exists(q1.filename)
        # assert os.path.exists(q2.filename)
        assert os.path.exists(q3.filename)



class r:
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
        print(q.queues)
        Benchmark.Stop()
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





























