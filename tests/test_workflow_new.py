# ##############################################################
# pytest -v -x --capture=no tests/test_workflow_new.py
# pytest -v  tests/test_workflow.py
# pytest -v --capture=no  tests/workflow.py::Test_queues::<METHODNAME>
# ##############################################################
import os.path
import shutil
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

global f_workflow  # this workflow is the one that is created from a pre-loaded file
global m_workflow  # this workflow is teh one that is created manually


class Test_workflow_new:

    def test_create_run(self):
        """
        This is simply to remove the ~/.cloudmesh/workflow directory in order to
        properly test the manually created workflow
        :return:
        """
        os.system("rm -r ~/.cloudmesh/workflow")
        exp = path_expand("~/.cloudmesh/workflow")
        shutil.rmtree(exp, ignore_errors=True)
        assert not os.path.isfile(exp)

    def test_load_workflow(self):
        """
        Testing if the a workflow can be made from loading a yaml file
        :return:
        """
        HEADING()
        global f_workflow
        Benchmark.Start()
        f_workflow = Workflow(filename="tests/workflow.yaml")
        Benchmark.Stop()
        print(f_workflow.graph)
        assert f_workflow.jobs is not None  # this tests that the load function actually added the nodes
        assert f_workflow.graph.edges is not None  # this tests that the load function actually added the edges

    def test_manual_workflow(self):
        """
        Testing if the initialization of a workflow can be made manually.
        :return:
        """
        HEADING()
        global m_workflow
        Benchmark.Start()
        m_workflow = Workflow()
        Benchmark.Stop()
        print(m_workflow.graph)
        assert len(m_workflow.graph.nodes) == 0   # this tests that the load function actually added the nodes. There are no nodes
        assert len(m_workflow.graph.edges) == 0  # this tests that the load function actually added the edges. There are no edges

    def test_set_up(self):
        """
        creates a manually done workflow. This workflow is saved under m_workflow
        :return: no return
        """
        HEADING()
        global m_workflow
        global username
        Benchmark.Start()

        login = {
            "localhost": {"user": "gregor", "host": "local"},
            "rivanna": {"user": f"{username}",
                        "host": "rivanna.hpc.virginia.edu"},
            "pi": {"user": "gregor", "host": "red"},
        }

        n = 0

        user = login["localhost"]["user"]
        host = login["localhost"]["host"]

        m_workflow.add_job(name="start", kind="local", user=user, host=host)
        m_workflow.add_job(name="end", kind="local", user=user, host=host)

        for host, kind in [("localhost", "local"),
                           ("rivanna", "remote-slurm"),
                           ("rivanna", "ssh")]:
            print("HOST:", host)
            user = login[host]["user"]
            host = login[host]["host"]
            m_workflow.add_job(name=f"job-{host}-{n}", kind=kind, user=user, host=host)
            n = n + 1
            m_workflow.add_job(name=f"job-{host}-{n}", kind=kind, user=user, host=host)
            n = n + 1
            m_workflow.add_job(name=f"job-{host}-{n}", kind=kind, user=user, host=host)
            n = n + 1

            first = n - 3
            second = n - 2
            third = n - 1
            m_workflow.add_dependencies(f"job-{host}-{first},job-{host}-{second}")
            m_workflow.add_dependencies(f"job-{host}-{second},job-{host}-{third}")
            m_workflow.add_dependencies(f"job-{host}-{third},end")
            m_workflow.add_dependencies(f"start,job-{host}-{first}")

        Benchmark.Stop()
        print(len(m_workflow.jobs) == n)

    def test_yaml_dump(self):
        HEADING()
        global f_workflow
        global m_workflow
        Benchmark.Start()
        f_data = f_workflow.yaml
        m_data = m_workflow.yaml
        print(f_data)
        print(m_data)
        Benchmark.Stop()
        assert "start" in m_data
        assert "end" in m_data
        assert "user" in m_data
        assert "a" in f_data
        assert "b" in f_data
        assert "jobs" in f_data

    def test_delete_job(self):
        HEADING()
        global f_workflow
        global m_workflow
        Benchmark.Start()
        f_workflow.remove_job(name='a')
        m_workflow.remove_job(name='job-local-1')
        assert 'a' not in f_workflow.graph.nodes
        assert 'job-local-1' not in m_workflow.graph.nodes

class rest:

    def test_json_dump(self):
        HEADING()
        global f_workflow
        global m_workflow
        Benchmark.Start()
        m_workflow.json(filepath='~/experiment/out-file.JSON')
        f_workflow.json(filepath='~/experiment/out-file.JSON')
        Benchmark.Stop()
        assert os.path.exists(path_expand('~/experiment/out-file.JSON')) is True
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
        assert 'start', 'job-local-1' in parents
