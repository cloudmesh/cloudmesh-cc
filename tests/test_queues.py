###############################################################
# pytest -v --capture=no tests/test_queues.py
# pytest -v  tests/test_queues.py
# pytest -v --capture=no  tests/test_queues.py::TestQueues::<METHODNAME>
###############################################################
import os.path
from pprint import pprint
import shelve
import pytest

from cloudmesh.common.Printer import Printer
from cloudmesh.cc.queue import Queues
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.util import path_expand

kind = "yamldb"
# kind = "shelve"
q = None

def shelve_name(prefix):
    if os_is_windows() or os_is_mac():
        return path_expand(prefix)
    else:
        return path_expand(f"{prefix}.db")

@pytest.mark.incremental
class TestQueues:
    def test_shelve_open_and_close(self):
        HEADING()
        Benchmark.Start()
        name = shelve_name("computers")
        computers = shelve.open(name)
        computers['temperature'] = {
            'red': 80,
            'blue': 40,
            'yellow': 50,
        }
        print(computers["temperature"])
        assert computers["temperature"]["red"] == 80
        computers.close()
        Benchmark.Stop()
        assert os.path.exists("computers.db")

    def test_shelve_read(self):
        HEADING()
        name = shelve_name("computers")
        computers = shelve.open(name)
        Benchmark.Start()
        temperature = computers['temperature']
        Benchmark.Stop()
        print('Initial temperature:')
        pprint(temperature)
        assert computers['temperature']['red'] == 80
        computers.close()
        # Alison: note that this is the code for shelve database remove() method
        if os_is_windows():
            os.remove("computers.bak")
            os.remove("computers.dat")
            os.remove("computers.dir")
        else:
            os.remove("computers.db")

class f:

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
        print(q)
        # pprint(q.queues)
        n = []
        for queue in q.queues:
            for job in q.queues[queue]:
                n.append(q.queues[queue][job])

        # print(Printer.list(n))

        # for f in ['yaml', 'json', 'csv', 'html', 'table']:

        # print(Printer.write(n, output=f))

        # print(q.config)
        # print(Printer.attribute(q.config))
        # print(Printer.attribute(q.config, output='json'))

        # pprint(n)
        assert len(q.get("local")) == 3

    def test_remove(self):
        HEADING()
        global q
        Benchmark.Start()
        print('Before removal: ')
        print()
        print(q.queues)
        q.remove('local')
        Benchmark.Stop()
        print("After removal: ")
        print()
        print(q.queues)
        assert len(q.queues) == 1  # this is because there were 2 queues and now there is only one.
        print()

    def test_list(self):
        HEADING()
        global q
        q.create(name='local')
        q.add(name='local', job='job-1', command='pwd')
        q.add(name='local', job='job-2', command='ls')
        q.add(name='local', job='job-3', command='hostname')
        Benchmark.Start()
        q.list()  # appears to list only the higher level queues, not everything within the queues
        Benchmark.Stop()
        assert len(q.queues) == 2

    def test_run(self):
        HEADING()
        global q
        print('Everything to be run: ')
        Benchmark.Start()
        q.run(scheduler='fifo')
        print('Everything that has been run: ')
        pprint(q.queues)
        Benchmark.Stop()
        assert q.counter == 6

    def test_get(self):
        HEADING()
        global q
        Benchmark.Start()
        job = q.db.get_job(queue='local', name='job-1')
        print(job)
        Benchmark.Stop()
