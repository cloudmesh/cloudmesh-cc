#######################################
# pytest -v -x --capture=no tests/test_workflow_jackson.py
# pytest -v  tests/test_workflow.py
# pytest -v --capture=no  tests/workflow.py::Test_queues::<METHODNAME>
###############################################################'
import os.path
from pprint import pprint
import shelve
import pytest

from cloudmesh.cc.workflow_jackson import Workflow
from cloudmesh.cc.queue import Queues
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.Shell import Shell
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
            "localhost": {"user": "gregor", "host": "local"},
            "rivanna": {"user": f"{user}", "host": "rivanna"},
            "pi": {"user": "gregor", "host": "red"},
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

    def test_add_sh_files(self):
        HEADING()
        global w
        nodes = w.jobs
        node = w.job(name='start')
        print(node)
        print(type(node))
        print(type(nodes))
        print(nodes)
        jobs = []
        for name in range(0, len(nodes)):
            job = nodes[name]
            jobs.append(job)

        # now we have the names of all of the jobs
        # we will create a method to cd into the correct directory and create
        # a .sh file with a bunch of stuff in it

        for name in jobs:
            print(name)
            word = name.name
            print('AAAAAAAAAAAAAAA', word)
            if name.host == 'localhost':
                directory = f'~/experiment/{word}'
                command1 = f' cd {directory} && touch {word}.sh'
                command2 = f'echo "#! /bin/bash\nhostname\nls\npwd" >> {word}.sh'

                os.system(command1)
                os.system(command2)

            elif name.host == 'rivanna':
                directory = f'experiment/{word}'
                host = name.host
                user = name.username
                print('USER', user)
                print('HOST', host)
                print(type(name))
                name.mkdir_remote
                command = f'ssh {user}@{host}.hpc.virginia.edu && ' \
                          f'cd {directory} && ' \
                          f'touch {word}.sh && ' \
                          f'echo "#! /bin/bash\nhostname\nls\npwd" ' \
                          f'>> {word}.sh'
                print(command)
                os.system(f'{command} &')


class rest:

    def test_show(self):
        HEADING()
        global w
        w.graph.save(filename="/tmp/test-dot.svg", colors="status",
                     layout=nx.circular_layout, engine="dot")
        # Shell.browser("/tmp/test-dot.svg")
        # assert os.path.exists("~/tmp/test-dot.svg") == True

    def test_get_node(self):
        HEADING()
        global w
        Benchmark.Start()
        s1 = w["start"]
        s2 = w.job("start")
        Benchmark.Stop()
        print(s1)
        assert s1 == s2

    def test_table(self):
        HEADING()
        global w
        Benchmark.Start()
        print(w.table)
        Benchmark.Stop()
        assert True

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

    def test_benchmark(self):
        HEADING()
        # StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
