#######################################
# pytest -v -x --capture=no tests/test_workflow_jackson.py
# pytest -v  tests/test_workflow.py
# pytest -v --capture=no  tests/workflow.py::Test_queues::<METHODNAME>
###############################################################'
import os
from os.path import exists as file_exists
import time
from pprint import pprint
import shelve
import pytest

from cloudmesh.cc.workflow_jackson import Workflow
from cloudmesh.cc.queue import Queues
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
import networkx as nx


global w
global user
user = input("Please enter your Rivanna(computing) ID here: ")
"""
    This is a python file to test to make sure the workflow class works.
    It will draw upon the the test_queues file, because there is a file that
    was created with a bunch of jobs. 
"""


class Test_workflow:

    def test_set_up(self):
        """
        establishing a queues object, saving 2 queues to it, each with 10 jobs
        :return: no return
        """
        HEADING()
        global w
        global user
        Benchmark.Start()
        w = Workflow()

        login = {
            "localhost": {"user": f"{user}", "host": "local"},
            "rivanna": {"user": f"{user}", "host": "rivanna"},
            "pi": {"user": f"{user}", "host": "red"},
        }

        n = 0

        user = login["localhost"]["user"]
        host = login["localhost"]["host"]

        w.add_job(name="start", kind="local", user=user, host=host)
        w.add_job(name="end", kind="local", user=user, host=host)

        for host, kind in [("localhost", "local"),
                           ("rivanna", "ssh")]:
            print("HOST:", host)
            user = login[host]["user"]
            host = login[host]["host"]
            w.add_job(name=f"job-{n}", kind=kind, user=user, host=host)
            n = n + 1
            w.add_job(name=f"job-{n}", kind=kind, user=user, host=host)
            n = n + 1
            w.add_job(name=f"job-{n}", kind=kind, user=user, host=host)
            n = n + 1

            first = n - 3
            second = n - 2
            third = n - 1
            w.add_dependencies(f"job-{first},job-{second}")
            w.add_dependencies(f"job-{second},job-{third}")
            w.add_dependencies(f"job-{third},end")
            w.add_dependencies(f"start,job-{first}")

        Benchmark.Stop()
        print(w.jobs)
        print(len(w.jobs) == n)

    def test_sync(self):
        HEADING()
        global w
        nodes = w.jobs
        print(nodes)
        Benchmark.Start()
        for job in nodes:
            print(job.name)
            print(job.host)
            print(job.username)
            print(job.directory)
            job.sync(f"~/cm/cloudmesh-cc/job-tests/tests/{job.name}.sh")
        Benchmark.Stop()
        for job in nodes:
            # all this checks is if the file exists in the cloudmesh directory
            command = f'cp /Users/jacksonmiskill/cm/cloudmesh-cc/job-tests/tests/{job.name}.sh .'
            print(command)
            os.system(command)
            file = f"./{job.name}.sh"
            print(file)
            r = os.path.isfile(file)
            print(r)
            assert r == True

    def test_get_node(self):
        HEADING()
        global w
        job = input('Enter a job that has been created that you want to see exists: ')
        Benchmark.Start()
        start = w.job(job)
        s2 = start.name
        Benchmark.Stop()
        print(s2)
        assert s2 == job

    def test_table(self):
        HEADING()
        global w
        Benchmark.Start()
        print(w.table)
        Benchmark.Stop()
        assert True

class rest:

    def test_order(self):
        HEADING()
        global w
        Benchmark.Start()
        order = w.sequential_order()
        Benchmark.Stop()
        print(order)
        assert len(order) == len(w.jobs)

    def test_run(self):
        HEADING()
        s1 = w.job("start")
        before = s1['status']
        print(before)
        Benchmark.Start()
        w.run()
        Benchmark.Stop()
        s2 = w.job('start')
        after = s2['status']
        print(after)


class todo:

    def test_show(self):
        HEADING()
        global w
        w.graph.save(filename="/tmp/test-dot.svg", colors="status",
                     layout=nx.circular_layout, engine="dot")
        Shell.browser("/tmp/test-dot.svg")
        assert os.path.exists("~/tmp/test-dot.svg") == True

    def test_benchmark(self):
        HEADING()
        # StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
