###############################################################
# pytest -v --capture=no tests/test_db_yaml.py
# pytest -v  tests/test_db_yaml.py
# pytest -v --capture=no  tests/test_db_yaml.py::Test_db_yaml::<METHODNAME>
###############################################################
import os.path

import pytest

from cloudmesh.cc.db.yamldb.database import Database
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING


@pytest.mark.incremental
class Test_db_yaml:

    """
    def yaml_open_and_close():
    def yaml_read()
    def test_create
    def test_add
    def test_delete
    def test_remove
    def test_save()
    def test_benchmark()
    """

    def test_create(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        db.clear()
        print(db.filename)
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

    def

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc-db")
