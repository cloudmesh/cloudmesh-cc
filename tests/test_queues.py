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
from pathlib import Path
from cloudmesh.common.util import banner

banner(Path(__file__).name, c = "#", color="RED")

kind = "yamldb"
# kind = "shelve"
q = None


@pytest.mark.incremental
class TestQueues:

    def test_create(self):
        HEADING()
        global q
        Benchmark.Start()
        q = Queues(filename='~/.cloudmesh/queue/test.yamldb')
        q.create(name='local')
        q.create(name='rivanna')
        Benchmark.Stop()
        # print(q.info())
        assert 'local' in q.queues
        assert os.path.exists(path_expand("~/.cloudmesh/queue/test.yamldb"))


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

        for f in ['yaml', 'json', 'csv', 'html', 'table']:

            print(Printer.write(n, output=f))

        print(Printer.attribute(q.config))
        print(Printer.attribute(q.config, output='json'))

        assert len(q.get("local")) == 3
        assert q["local"]["job-1"]["name"] == "job-1"


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
