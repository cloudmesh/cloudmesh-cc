# ######################################
# pytest -v -x --capture=no tests/test_workflow_jackson.py
# pytest -v  tests/test_workflow.py
# pytest -v --capture=no  tests/workflow.py::Test_queues::<METHODNAME>
# ##############################################################'
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

user = input("Please enter your Rivanna(computing) ID here: ")
"""
    This is a python file to test to make sure the workflow class works.
    It will draw upon the the test_queues file, because there is a file that
    was created with a bunch of jobs. 
"""


class Test_workflow:



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
            assert r



