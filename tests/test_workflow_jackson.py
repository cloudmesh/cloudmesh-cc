###############################################################
# pytest -v -x --capture=no tests/test_workflow_jackson.py
# pytest -v  tests/test_workflow.py
# pytest -v --capture=no  tests/workflow.py::Test_queues::<METHODNAME>
###############################################################'
import os.path
from pprint import pprint
import shelve
import pytest

from cloudmesh.cc.dirworkflow.workflow_jackson import Workflow
from cloudmesh.cc.queue import Queues
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.Shell import Shell
import networkx as nx

global w
"""
    This is a python file to test to make sure the workflow class works.
    It will draw upon the the test_queues file, because there is a file that
    was created with a bunch of jobs. 
"""

class Test_workflow:

    def test_create(self):
        HEADING()
        global w
        Benchmark.Start()
        w = Workflow(name='workflow', filename='~/.cloudmesh/workflow/workflow')
        Benchmark.Stop()
        assert w.name == 'workflow'

    def test_add_jobs(self):
        HEADING()
        global w
        Benchmark.Start()
        w.add_job(name='job1', user='jcm4bsq', host='localhost', label='run')
        w.add_job(name='job2', user='jcm4bsq', host='localhost', label='run')
        w.add_job(name='job3', user='jcm4bsq', host='localhost', label='run')
        w.add_job(name='job4', user='jcm4bsq', host='localhost', label='run')
        w.add_job(name='job5', user='jcm4bsq', host='localhost', label='run')
        w.add_job(name='job6', user='jcm4bsq', host='rivanna', label='run')
        w.add_job(name='job7', user='jcm4bsq', host='rivanna', label='run')
        w.add_job(name='job8', user='jcm4bsq', host='rivanna', label='run')
        w.add_job(name='job9', user='jcm4bsq', host='rivanna', label='run')
        w.add_job(name='job10', user='jcm4bsq', host='rivanna', label='run')
        Benchmark.Stop()
        assert w.get_job('job1').host == 'localhost'
        assert w.get_job('job7').user == 'jcm4bsq'

class rest:

    pass