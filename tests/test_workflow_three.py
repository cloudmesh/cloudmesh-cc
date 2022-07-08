# ##############################################################
# pytest -v -x --capture=no tests/test_workflow_three.py
# pytest -v  tests/test_workflow.py
# pytest -v --capture=no  tests/workflow.py::Test_queues::<METHODNAME>
# ##############################################################
import os.path
from pprint import pprint
import shelve
import pytest

from cloudmesh.cc.workflow import Workflow
from cloudmesh.cc.queue import Queues
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.Shell import Shell
import networkx as nx
from cloudmesh.common.variables import Variables
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
import json
from cloudmesh.common.util import path_expand

"""
    This is a python file to test to make sure the workflow class works.
    It will draw upon the the test_queues file, because there is a file that
    was created with a bunch of jobs. 
"""

variables = Variables()

name = "run"

if "host" not in variables:
    host = "rivanna.hpc.virginia.edu"
else:
    host = variables["host"]

username = variables["username"]

if username is None:
    Console.warning("Username not entered. Please enter a username,\n"
                    "or no input to quit.\n")
    username = input()
    if username == '':
        print("quitting")
        print("quitting")
        quit()
    variables["username"] = username

class Test_workflow:

    def test_load_workflow(self):
        HEADING()
        global w
        Benchmark.Start()
        w = Workflow()
        w.load("tests/workflow.yaml")
        Benchmark.Stop()
        print(w.graph)

    def test_set_up(self):
        """
        establishing a queues object, saving 2 queues to it, each with 10 jobs
        :return: no return
        """
        HEADING()
        global w
        global username
        Benchmark.Start()
        w = Workflow()

        login = {
            "localhost": {"user": "gregor", "host": "local"},
            "rivanna": {"user": f"{username}", "host": "rivanna.hpc.virginia.edu"},
            "pi": {"user": "gregor", "host": "red"},
        }

        n = 0

        user = login["localhost"]["user"]
        host = login["localhost"]["host"]

        w.add_job(name="start", kind="local", user=user, host=host)
        w.add_job(name="end", kind="local", user=user, host=host)

        for host, kind in [("localhost", "local"),
                           ("rivanna", "remote-slurm"),
                           ("rivanna", "ssh")]:
            print("HOST:", host)
            user = login[host]["user"]
            host = login[host]["host"]
            w.add_job(name=f"job-{host}-{n}", kind=kind, user=user, host=host)
            n = n + 1
            w.add_job(name=f"job-{host}-{n}", kind=kind, user=user, host=host)
            n = n + 1
            w.add_job(name=f"job-{host}-{n}", kind=kind, user=user, host=host)
            n = n + 1

            first = n - 3
            second = n - 2
            third = n - 1
            w.add_dependencies(f"job-{host}-{first},job-{host}-{second}")
            w.add_dependencies(f"job-{host}-{second},job-{host}-{third}")
            w.add_dependencies(f"job-{host}-{third},end")
            w.add_dependencies(f"start,job-{host}-{first}")

        Benchmark.Stop()
        print(len(w.jobs) == n)

    def test_yaml_dump(self):
        HEADING()
        global w
        Benchmark.Start()
        data = w.yaml
        print(data)
        Benchmark.Stop()
        assert "start" in data
        assert "end" in data
        assert "user" in data

    def test_json_dump(self):
        HEADING()
        global w
        Benchmark.Start()
        w.json(filepath='~/experiment/out-file.JSON')
        Benchmark.Stop()
        assert os.path.exists(path_expand('~/experiment/out-file.JSON')) == True
        f = open(path_expand('~/experiment/out-file.JSON'))
        data = json.load(f)
        print(type(data))
        print('AAAAAAA', data)
        # assert 'created:' in data
        # assert 'end' in data
        # assert 'user' in data
        f.close()

    # the issue with the json method is that the json built in method does
    # not allow for datetime values. Not sure how to get around this.

    def test_predecessor(self):
        HEADING()
        Benchmark.Start()
        parents = w.predecessor(name='job-local-2')
        print(parents)
        Benchmark.Stop()
        assert 'start','job-local-1' in parents
