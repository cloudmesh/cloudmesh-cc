###############################################################
# pytest -v --capture=no tests/test_dbshelf.py
# pytest -v  tests/test_dbshelf.py
# pytest -v --capture=no  tests/test_dbshelf..py::Test_dbshelf::<METHODNAME>
###############################################################
import os.path
import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.cc.db.shelve.database import Database
import shelve
from pprint import pprint
import sys


@pytest.mark.incremental
class Test_dbshelf:
    def test_shelveopen(self):
        HEADING()
        Benchmark.Start()
        computers = shelve.open('computers.db')
        computers['temperature'] = {
            'red': 80,
            'blue': 40,
            'yellow': 50,
        }
        print('Initial temperature:')
        pprint(computers['temperature'])
        computers.close()

        # develop a read function
        c = shelve.open('computers.db')
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
        db.info()
        print(db.data["queues"])
        Benchmark.Stop()
        assert os.path.exists(f"{db.filename}.dat")
        assert len(db.data["queues"]) == 0

    def test_add(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        db.data["queues"] = {'name': 'red'}
        db.save()
        db.info()
        print(db.data["queues"])
        Benchmark.Stop()
        assert os.path.exists(f"{db.filename}.dat")
        assert len(db.data["queues"]) == 1
        assert db.data["queues"]["name"] == "red"

    def test_delete(self):
        HEADING()
        Benchmark.Start()
        db = Database()
        db.__delitem__("name")

        db.save()
        db.info()
        print(db.data["queues"])
        Benchmark.Stop()
        assert len(db.data["queues"]) == 0
        assert "name" not in db.data["queues"]

class rest:

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


# computers = shelve.open('computers1.db')
# computers['temperature'] = {
#     'red': 80,
#     'blue': 40,
#     'yellow': 50,
# }
# print('Initial temperature:')
# pprint(computers['temperature'])
# computers.close()
#
# # develop a read function
# c=shelve.open('computers1.db')
# pprint(str(c))
# pprint(c['temperature'])
#
# assert c['temperature']['red']==80
#
# with shelve.open('computers.db') as computers:
#     computers['temperature'] = {
#         'red': 80,
#         'blue': 40,
#         'yellow': 50,
#     }
#     print('Initial temperature:')
#     pprint(computers['temperature'])
#
#
# with shelve.open('computers.db') as computers:
#
#     #c = computers['temperature']
#     #c['green'] = 101
#     #computers['temperature'] = c
#
#     computers['temperature']['blue'] = 101
#     # del computers['temperature']['yellow']
#     print()
#     print('Modified temperature:')
#     pprint(computers['temperature'])
#
