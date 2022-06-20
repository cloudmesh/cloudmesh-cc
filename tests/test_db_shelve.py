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

    def test_shelve_open_and_close(self):
        HEADING()
        Benchmark.Start()
        computers = shelve.open('computers')
        computers['temperature'] = {
            'red': 80,
            'blue': 40,
            'yellow': 50,
        }
        computers.close()
        Benchmark.Stop()

    def test_shelve_read(self):
        HEADING()
        computers = shelve.open('computers')
        Benchmark.Start()
        temperature = computers['temperature']
        Benchmark.Stop()
        print('Initial temperature:')
        pprint(temperature)
        assert computers['temperature']['red'] == 80
        computers.close()


    def test_create(self):
        HEADING()
        Shell.rmdir("~/.cloudmesh/queue")
        Benchmark.Start()
        db = Database()
        # db.clear()
        # db.save()
        Benchmark.Stop()
        print(db)
        assert os.path.exists(db.filename)
        assert len(list(db.data.keys())) == 0

class rest:
    def test_add(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        db.data["queues"] = {'name': 'red'}
        db.save()
        db.info()
        Benchmark.Stop()
        print(db.data["queues"])
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
        db = Database()
        db.remove()
        Benchmark.Stop()
        assert not os.path.exists(db.filename)

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
