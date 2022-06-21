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
        # Alison: note that this is the code for shelve database remove() method
        if os_is_windows():
            os.remove("computers.bak")
            os.remove("computers.dat")
            os.remove("computers.dir")
        else:
            os.remove("computers.db")

    def test_create(self):
        HEADING()
        # Shell.rmdir("~/.cloudmesh/queue")
        # input()
        Benchmark.Start()
        db = Database()
        db.clear()
        Benchmark.Stop()
        print(db)
        assert os.path.exists(db.filename)
        assert len(list(db.data.keys())) == 0
        db.close()

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
        db.close()

    def test_delete(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        db.data["queues"].pop("name")
        # db.delete("queues")
        db.save()
        db.info()
        Benchmark.Stop()
        assert len(db.data["queues"]) == 0
        db.close()

    def test_remove(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        filename = db.filename
        db.remove()
        db.close()
        Benchmark.Stop()
        assert not os.path.exists(filename)

    def test_save(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        db["queue.a"] = {"name": "gregor"}
        db["queue.b"] = {"name": "gregor"}
        db["queue.c"] = {"name": "gregor"}
        db.close()

        n = Database()
        Benchmark.Stop()
        assert n["queue.a"]["name"] == "gregor"
        assert n["queue.b"]["name"] == "gregor"

        print(n)
        n.close()

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
