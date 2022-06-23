###############################################################
# pytest -v --capture=no tests/test_queues.py
# pytest -v  tests/test_queues.py
# pytest -v --capture=no  tests/test_queues.py::Test_queues::<METHODNAME>
###############################################################
import os.path
from pprint import pprint

import pytest

from cloudmesh.common.Printer import Printer
from cloudmesh.cc.queue import Queues
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING

kind = "yamldb"
# kind = "shelve"
q = None

@pytest.mark.incremental
class Test_queues:

    def test_create(self):
        HEADING()
        global q
        Benchmark.Start()
        q = Queues(filename='~/.cloudmesh/queue/queuetest1', database=kind)
        q.create(name='local')
        q.create(name='rivanna')
        Benchmark.Stop()
        # print(q.info())
        assert 'local' in q.queues
        print()

    def test_filename(self):
        if kind == "shelve":
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
        else:
            assert True

    def test_add(self):
        HEADING()
        global q
        Benchmark.Start()
        q.add(name='local', job='job-1', command='pwd')
        q.add(name='local', job='job-2', command='ls')
        q.add(name='local', job='job-3', command='hostname')
        q.add(name='rivanna', job='job-1', command='pwd')
        q.add(name='rivanna', job='job-2', command='ls')
        q.add(name='rivanna', job='job-3', command='hostname')
        Benchmark.Stop()
        # print(q)
        #pprint(q.queues)
        n = []
        for queue in q.queues:
            for job in q.queues[queue]:
                n.append(q.queues[queue][job])

        print(Printer.list(n))

        for f in ['yaml', 'json', 'csv', 'html', 'table']:

            print(Printer.write(n, output=f))

        print(q.config)
        print(Printer.attribute(q.config))
        print(Printer.attribute(q.config, output='json'))


        # pprint(n)
        assert len(q.get("local")) == 3


class r:

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

    """
        def test_remove(self):
        HEADING()
        global q
        Benchmark.Start()
        print('Before removal: ')
        print()
        print(q)
        q.remove('local')
        Benchmark.Stop()
        print("After removal: ")
        print()
        print(q)
        assert len(q.queues) == 1  # this is because there were 2 queues and now there is only one.
        print()
    """

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

    """
        def test_list(self):
        HEADING()
        global q
        q.create(name='local')
        q.add(name='local', job='job-1', command='pwd')
        q.add(name='local', job='job-2', command='ls')
        q.add(name='local', job='job-3', command='hostname')
        Benchmark.Start()
        q.list()  #appears to list only the higher level queues, not everything within the queues
        Benchmark.Stop()
        assert len(q.queues) == 2
    """

    def test_run(self):
        raise NotImplementedError
    """
        def test_run(self):
        HEADING()
        global q
        print('Everything to be run: ')
        pprint(q)
        Benchmark.Start()
        q.run(scheduler='fifo')
        print('Everything that has been run: ')
        pprint(q)
        Benchmark.Stop()
        assert q.counter == 6
    """
