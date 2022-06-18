###############################################################
# pytest -v --capture=no tests/test_db_shelve.py
# pytest -v  tests/test_db_shelve.py
# pytest -v --capture=no  tests/test_db_shelve.py::Test_db_shelve::<METHODNAME>
###############################################################
import os.path
import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.cc.db.shelve.database import Database
from cloudmesh.common.systeminfo import os_is_mac, os_is_windows
import shelve
from pprint import pprint
import sys


@pytest.mark.incremental
class Test_db_shelve:

    def test_shelveopen(self):
        HEADING()
        Benchmark.Start()
        computers = shelve.open('computers')
        computers['temperature'] = {
            'red': 80,
            'blue': 40,
            'yellow': 50,
        }
        print('Initial temperature:')
        pprint(computers['temperature'])
        computers.close()

        # develop a read function
        c = shelve.open('computers')
        pprint(str(c))
        pprint(c['temperature'])

        Benchmark.Stop()
        assert c['temperature']['red'] == 80

    def test_create(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        db.clear()
        db.save()
        # db.info()
        print(db)
        Benchmark.Stop()
        assert os.path.exists(db.filename)
        assert len(list(db.data.keys())) == 0

    def test_add(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        db.data["queues"] = {'name': 'red'}
        db.save()
        db.info()
        print(db.data["queues"])
        Benchmark.Stop()
        assert os.path.exists(db.filename)
        assert len(db.data["queues"]) == 1
        assert db.data["queues"]["name"] == "red"

    def test_delete(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        db["queues"].pop("name")
        db.save()
        db.info()
        Benchmark.Stop()
        assert len(db["queues"]) == 0

    def test_remove(self):
        HEADING()
        Benchmark.Start()
        db1 = Database()
        db1.remove()
        Benchmark.Stop()
        assert not os.path.exists(db1.filename)

    def test_save(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        db["queue.a"] = {"name": "gregor"}
        db["queue.b"] = {"name": "gregor"}
        db["queue.c"] = {"name": "gregor"}

        n = Database()
        Benchmark.Stop()
        assert n["queue.a"]["name"] == "gregor"
        assert n["queue.b"]["name"] == "gregor"

        print(n)


    """
    def test_queue_create(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms cc create localhost", shell=True)
        Benchmark.Stop()
        VERBOSE(result)
        assert "quit" in result
        assert "clear" in result
    """

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc-shelve")
