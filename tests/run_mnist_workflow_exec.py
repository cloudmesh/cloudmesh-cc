# ##############################################################
# pytest -v -x --capture=no tests/run_mnist_workflow_exec.py
# pytest -v  tests/test_workflow_exec.py
# pytest -v --capture=no  tests/run_mnist_workflow_exec.py::TestWorkflowLocal::<METHODNAME>
# ##############################################################
import os.path
import shutil
from pathlib import Path
import pytest

import networkx as nx

from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell
from cloudmesh.common.variables import Variables
from pprint import pprint
# from utilities import set_host_user

"""
This is a python file to test the implementation of workflow in running the 
mnist files. 
"""

location = Shell.map_filename("./tests/mnist").path
os.chdir(location)


@pytest.mark.incremental
class TestMnist:

    def test_mnist(self):
        HEADING()
        Shell.rm("mnist.yaml")
        Shell.copy_file('./source-mnist-exec.yaml', 'mnist.yaml')
        filename = Shell.map_filename("./mnist.yaml").path
        r = Shell.ls()
        pprint(r)

        w = Workflow(filename=filename)
        w.load(filename=filename)
        print (w)
        #w.load(filename=filename)
        #w.display(name='mnist')
        # w.run_topo(show=True)