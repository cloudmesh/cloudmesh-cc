###############################################################
# pytest -v --capture=no tests/test_db.py
# pytest -v  tests/test_db.py
# pytest -v --capture=no  tests/test_db..py::Test_db::<METHODNAME>
###############################################################
import os.path

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
# from cloudmesh.cc.database import QDatabase
from cloudmesh.cc.database import Database


@pytest.mark.incremental
class TestConfig:

    def test_create(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        db.clear()
        print (db.filename)
        Benchmark.Stop()
        assert os.path.exists(db.filename)

    def test_save(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        db["queue.a"] = {"name": "gregor"}
        db["queue.b"] = {"name": "gregor"}
        db["queue.c"] = {"name": "gregor"}


        n = Database()
        Benchmark.Stop()
        assert n["queue.a.name"] == "gregor"
        assert n["queue.b.name"] == "gregor"

        print(n)





"""
class a:
    def test_queue_create(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms cc create localhost", shell=True)
        Benchmark.Stop()
        VERBOSE(result)
        assert "quit" in result
        assert "clear" in result

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cmd5")
"""